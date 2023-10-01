import difflib
import logging
import re
from dataclasses import dataclass
from typing import List, Union, Tuple, Any
from typing import Optional
from uuid import UUID

from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema.output import GenerationChunk, ChatGenerationChunk

from ghostcoder.actions.base import BaseAction
from ghostcoder.actions.write_code.prompt import get_implement_prompt, ROLE_PROMPT, FEW_SHOTS_PYTHON
from ghostcoder.codeblocks import create_parser, CodeBlockType
from ghostcoder.filerepository import FileRepository
from ghostcoder.ipython_callback import DisplayCallback
from ghostcoder.llm.base import LLMWrapper
from ghostcoder.schema import Message, FileItem, Stats, TextItem, UpdatedFileItem, CodeItem
from ghostcoder.utils import is_complete

logger = logging.getLogger(__name__)

@dataclass
class CodeBlock:
    content: str
    language: str = None
    file_path: str = None


class StreamCallback(BaseCallbackHandler):

    def __init__(self, callback: DisplayCallback):
        self.callback = callback

    def on_llm_new_token(
        self,
        token: str,
        *,
        chunk: Optional[Union[GenerationChunk, ChatGenerationChunk]] = None,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        if self.callback:
            self.callback.ai_stream(token)


def get_file_item(items: list, file_path: str):
    equal_match = [item for item in items if "file" in item.type and item.file_path == file_path]
    if equal_match:
        return equal_match[0]

    similar_matches = [item for item in items if "file" in item.type and file_path in item.file_path]
    if len(similar_matches) == 1:
        return similar_matches[0]
    else:
        logger.info(f"Found {len(similar_matches)} similar matches for {file_path}: {similar_matches}, expected one")

    return None


def extract_response_parts(response: str) -> List[Union[str, CodeBlock]]:
    """
    This function takes a string containing text and code blocks.
    It returns a list of CodeBlock, FileBlock, and non-code text in the order they appear.

    The function can parse two types of code blocks:

    1) Backtick code blocks with optional file path:
    F/path/to/file
    ```LANGUAGE
    code here
    ```

    2) Square-bracketed code blocks with optional file path:
    /path/to/file
    [LANGUAGE]
    code here
    [/LANGUAGE]


    Parameters:s
    text (str): The input string containing code blocks and text

    Returns:
    list: A list containing instances of CodeBlock, FileBlock, and non-code text strings.
    """

    combined_parts = []

    # Normalize line breaks
    response = response.replace("\r\n", "\n").replace("\r", "\n")

    # Regex pattern to match code blocks
    block_pattern = re.compile(
        r"```(?P<language1>\w*)\n(?P<code1>.*?)\n```|"  # for backtick code blocks
        r"\[(?P<language2>\w+)\]\n(?P<code2>.*?)\n\[/\3\]",  # for square-bracketed code blocks
        re.DOTALL
    )

    # Define pattern to find files mentioned with backticks
    file_pattern = re.compile(r"`([\w/]+\.\w{1,4})`")

    # Pattern to check if the filename stands alone on the last line
    standalone_file_pattern = re.compile(r'^(?:"|`)?(?P<filename>[\w\s\-/\\]+\.\w{1,4})(?:"|`)?$', re.IGNORECASE)

    last_end = 0

    for match in block_pattern.finditer(response):
        start, end = match.span()

        preceding_text = response[last_end:start].strip()
        preceding_text_lines = preceding_text.split("\n")

        file_path = None

        non_empty_lines = [line for line in preceding_text_lines if line.strip()]
        if non_empty_lines:
            last_line = non_empty_lines[-1].strip()

            filename_match = standalone_file_pattern.match(last_line)
            if filename_match:
                file_path = filename_match.group("filename")
                # Remove the standalone filename from the preceding text
                idx = preceding_text_lines.index(last_line)
                preceding_text_lines = preceding_text_lines[:idx]
                preceding_text = "\n".join(preceding_text_lines).strip()

            # If not found, then check for filenames in backticks
            if not file_path:
                all_matches = file_pattern.findall(last_line)
                if all_matches:
                    file_path = all_matches[-1]  # Taking the last match from backticks
                    if len(all_matches) > 1:
                        logging.info(f"Found multiple files in preceding text: {all_matches}, will set {file_path}")

        # If there's any non-code preceding text, append it to the parts
        if preceding_text:
            combined_parts.append(preceding_text)

        if match.group("language1") or match.group("code1"):
            language = match.group("language1") or None
            content = match.group("code1").strip()
        else:
            language = match.group("language2").lower()
            content = match.group("code2").strip()

        code_block = CodeBlock(file_path=file_path, language=language, content=content)

        combined_parts.append(code_block)

        last_end = end

    remaining_text = response[last_end:].strip()
    if remaining_text:
        combined_parts.append(remaining_text)

    return combined_parts


def do_diff(file_path: str, original_content: str, updated_content: str) -> Optional[str]:
    return "".join(difflib.unified_diff(
        original_content.strip().splitlines(True),
        updated_content.strip().splitlines(True),
        fromfile=file_path, tofile=file_path, lineterm="\n"))


class CodeWriter(BaseAction):

    def __init__(self,
                 llm: LLMWrapper,
                 role_prompt: Optional[str] = None,
                 sys_prompt_id: Optional[str] = None,
                 sys_prompt: Optional[str] = None,
                 repository: FileRepository = None,
                 auto_mode: bool = False,
                 few_shot_prompt: bool = False,
                 guess_similar_files: bool = True,
                 expect_one_file: bool = False,
                 allow_hallucinated_files: bool = False,
                 callback: DisplayCallback = None,
                 tries: int = 2):
        if not sys_prompt:
            sys_prompt = get_implement_prompt(sys_prompt_id)
        super().__init__(llm, sys_prompt)
        self.llm = llm
        self.repository = repository
        self.auto_mode = auto_mode
        self.tries = tries
        self.role_prompt = role_prompt
        self.few_shot_prompt = few_shot_prompt
        self.guess_similar_files = guess_similar_files
        self.expect_one_file = expect_one_file
        self.allow_hallucinations = allow_hallucinated_files
        self.callback = callback

    def execute(self, incoming_messages: List[Message]) -> List[Message]:
        outgoing_messages = self._execute(incoming_messages=incoming_messages, retry=0)
        stats = [msg.stats for msg in outgoing_messages if msg.stats]
        use_log = ""
        if stats:
            total_usage = sum(stats[1:], stats[0])
            use_log = f"Used {total_usage.prompt_tokens} prompt tokens, {total_usage.prompt_tokens}. "
            if total_usage.total_cost:
                use_log += f"Total cost: {total_usage.total_cost}. "

        logger.info(f"Finished executing with {len(outgoing_messages)} messages. {use_log}")
        return outgoing_messages

    def _execute(self, incoming_messages: List[Message], retry: int = 0) -> List[Message]:
        file_items = []
        for message in incoming_messages:
            file_items_in_message = message.find_items_by_type(item_type="file")
            file_items.extend(file_items_in_message)

            updated_files = message.find_items_by_type(item_type="updated_file")
            for updated_file in updated_files:
                if not updated_file.invalid:
                    file_items.append(updated_file)

        if file_items:
            incoming_files = ""
            for file_item in file_items:
                incoming_files += f"\n- {file_item.to_log()}"
            logger.info(f"Incoming files:{incoming_files}")
        else:
            logger.info(f"No incoming files")

        try:
            result, stats = self.generate(messages=incoming_messages, callback=StreamCallback(callback=self.callback))
        except Exception as e: # TODO: Handle context_length_exceeded...
            return [Message(sender="Ghostcoder", items=[TextItem(text=str(e))])]

        blocks = extract_response_parts(result)

        retry_inputs = []

        items = []
        for block in blocks:
            if isinstance(block, CodeBlock):
                first_content = block.content[:40].replace("\n", "\\n")
                logger.debug(f"Received code block with file path `{block.file_path}` and language `{block.language}`: "
                             f"`{first_content}...`")
                stats.increment("code_block")

                if not block.file_path:
                    self.set_file_path_to_block(block, file_items, stats)

                if not block.file_path and self.expect_one_file and len(file_items) == 1:
                    code_block_count = sum(1 for block in blocks if (isinstance(block, CodeBlock)
                                                                     and not block.file_path
                                                                     and (block.language is None
                                                                          or block.language == file_items[0].language)))
                    if code_block_count == 1:
                        logger.debug(f"Found one code block with language {file_items[0].language} and no file path, "
                                     f"will assume it's the updated file {file_items[0].file_path}")
                        block.file_path = file_items[0].file_path

                if block.file_path:
                    already_updated_file_item = get_file_item(items, block.file_path)
                    if not already_updated_file_item:
                        original_file_item = get_file_item(file_items, block.file_path)

                    updated_file_item, retry_inputs_for_file = self.updated_file(
                        stats,
                        block,
                        already_updated_file_item or original_file_item,
                        file_items)
                    retry_inputs.extend(retry_inputs_for_file)

                    if already_updated_file_item and not updated_file_item.invalid:
                        already_updated_file_item.content = updated_file_item.content
                    elif updated_file_item:
                        items.append(updated_file_item)
                else:
                    items.append(CodeItem(content=block.content, language=block.language))
            else:
                logger.debug("Received text block: [{}...]".format(block[:25].replace("\n", "\\n")))
                items.append(TextItem(text=block))
                if self.has_not_closed_code_blocks(block):
                    # TODO: Handle if this is due to max token limit
                    stats.increment("not_closed_code_block")
                    retry_inputs.append(
                        TextItem(text="You responded with a incomplete code block. "
                                      "Please provide the contents of the whole file in a code block closed with ```."))

        updated_files_str = ""

        did_changes = False
        for item in items:
            if item.type == "updated_file":
                if not item.invalid and self.repository:
                    try:
                        diff = self.repository.update_file(item.file_path, item.content)
                        did_changes = bool(diff)
                        item.diff = diff
                        if not did_changes:
                            item.invalid = "no_change"
                    except Exception as e:
                        item.error = f"Failed to update file {item.file_path}: {e}"
                        stats.increment("failed_to_update_file")
                        logger.error(item.error)
                updated_files_str += f"\n- {item.to_log()}"

        if updated_files_str:
            logger.info(f"Updated files: {updated_files_str}")
        else:
            logger.info(f"No updated files")

        ai_message = Message(sender="AI", items=items, stats=stats)

        if self.callback:
            self.callback.display_message(ai_message)

        outgoing_messages = [ai_message]

        if self.auto_mode and retry_inputs:
            retry += 1
            retry_message = Message(sender="Ghostcoder", items=retry_inputs, auto=True)

            if self.callback:
                self.callback.display_message(retry_message)

            logger.info(f"Found invalid input in the response.\n {retry_message.to_prompt()}")
            outgoing_messages.append(retry_message)

            if retry < self.tries:
                logger.info(f"Retrying execution (try: {retry}/{self.tries})")
                outgoing_messages.extend(self._execute(
                    incoming_messages=incoming_messages + outgoing_messages,
                    retry=retry + 1))

        return outgoing_messages

    def set_file_path_to_block(self, block: CodeBlock, file_items: List[FileItem], stats: Stats):
        """Tries to find a file item that matches the code block."""

        if not self.guess_similar_files:
            return

        for file_item in file_items:
            if not file_item.language:
                continue

            if block.language and block.language != file_item.language:
                logger.debug(
                    f"Language in block [{block.language}] does not match language [{file_item.language}] file path {file_item.file_path}")
                continue

            try:
                parser = create_parser(file_item.language)
                original_block = parser.parse(file_item.content)
                updated_block = parser.parse(block.content)

                matching_blocks = original_block.get_matching_blocks(updated_block)
                if any(matching_block for matching_block in matching_blocks
                       if matching_block.type in [CodeBlockType.FUNCTION, CodeBlockType.CLASS]):
                    matching_content_str = "".join([f"\n- {block.content.strip()}" for block in matching_blocks])
                    logger.info(f"Code block has similarities to {file_item.file_path}, will assume it's the "
                                 f"updated file.\nSimilarities:{matching_content_str})")
                    stats.increment("guess_file_item")

                    block.file_path = file_item.file_path
                    block.language = file_item.language
            except Exception as e:
                logger.warning(
                    f"Could not parse file with {file_item.language} or code block with language {block.language}: {e}")

    def updated_file(self, stats: Stats, block: CodeBlock, existing_file_item: FileItem, file_items: List[FileItem]) -> Tuple[Optional[UpdatedFileItem], List[TextItem]]:
        logger.debug("Received file block: [{}]".format(block.file_path))
        stats.increment("file_item")

        retry_inputs = []

        warning = None
        updated_content = block.content
        invalid = None
        new = False

        # Don't merge and mark as invalid if the file is readonly
        if existing_file_item and existing_file_item.readonly:
            return UpdatedFileItem(
                file_path=existing_file_item.file_path,
                content=updated_content,
                invalid="readonly",
            ), retry_inputs

        # Don't merge and mark as invalid if hallucinated files isn't allowed
        if not existing_file_item and not self.allow_hallucinations:
            logger.info(f"Could not find file {block.file_path} in initial message")
            stats.increment("missing_file")
            available_files = ", ".join([f"`{f.file_path}`" for f in file_items])
            retry_inputs.append(TextItem(text=f"I only expected the following files in the response {available_files}. "
                                              f"But `{block.file_path} was returned."))
            return UpdatedFileItem(
                file_path=block.file_path,
                content=updated_content,
                invalid="hallucination",
            ), retry_inputs

        # Just return the updated content if original file is empty
        if existing_file_item and not existing_file_item.content:
            return UpdatedFileItem(
                file_path=existing_file_item.file_path,
                content=updated_content
            ), retry_inputs

        parser = None
        if block.language in ["python", "java", "typescript", "javascript"]:
            try:
                parser = create_parser(block.language)
            except Exception as e:
                logger.warning(f"Could not create parser for language {block.language}: {e}")

        if parser:
            try:
                updated_block = parser.parse(updated_content)
            except Exception as e:
                logger.warning(f"Could not parse updated  in {block.file_path}: {e}")
                stats.increment("invalid_code_block")
                retry_input = f"You returned a file with the following invalid code blocks: \n" + updated_content
                return None, [TextItem(text=retry_input)]

            error_blocks = updated_block.find_errors()
            if error_blocks:
                stats.increment("files_with_errors")
                logger.info("The updated file {} has errors. ".format(block.file_path))
                retry_inputs.append(
                    TextItem(text="You returned a file with syntax errors. Find them and correct them."))
                invalid = "syntax_error"
                for error_block in error_blocks:
                    retry_inputs.append(
                        CodeItem(language=block.language, content=error_block.to_string()))
            elif existing_file_item and not existing_file_item.readonly:
                original_block = parser.parse(existing_file_item.content)
                gpt_tweaks = original_block.merge(updated_block, first_level=True)

                stats.increment("merged_file")
                if gpt_tweaks:
                    stats.extra["gpt_tweaks"] = gpt_tweaks
                    stats.increment("did_gpt_tweaks")

                updated_content = original_block.to_string()
                merged_block = parser.parse(updated_content)
                error_blocks = merged_block.find_errors()
                if error_blocks:
                    stats.increment("merged_files_with_errors")
                    logger.info("The merged file {} has errors..".format(block.file_path))
                    retry_inputs.append(
                        TextItem(text="You returned a file with syntax errors. Find them and correct them."))
                    invalid = "syntax_error"
                    for error_block in error_blocks:
                        retry_inputs.append(FileItem(language=block.language, content=error_block.to_string(),
                                                     file_path=block.file_path))

        if not retry_inputs and not is_complete(updated_content):
            logger.info(f"The content in block [{block.file_path}] is not complete, will retry")
            stats.increment("not_complete_file")
            retry_inputs.append(
                TextItem(text=f"Return all code from the original code in the update file {block.file_path}."))
            invalid = "not_complete"

        if existing_file_item:
            block.file_path = existing_file_item.file_path
            diff = do_diff(file_path=block.file_path, original_content=existing_file_item.content,
                           updated_content=updated_content)
            if not diff:
                invalid = "no_change"
                stats.increment("no_change")

            if existing_file_item.readonly:
                invalid = "readonly"
                stats.increment("updated_readonly_file")

        elif self.repository.get_file_content(block.file_path):
            # TODO: Check in context if the file is mentioned or listed in earlier messages
            logger.info(f"{block.file_path} not found in initial message but exists in repo, will assume"
                         f"that it's a hallucination and ignore the file.")
            stats.increment("hallucinated_file")
            invalid = "hallucinated"
        else:
            stats.increment("new_file")
            logger.debug(f"{block.file_path} not found in initial message, assume new file.")
            new = True

        return UpdatedFileItem(
            file_path=block.file_path,
            content=updated_content,
            error=warning,
            invalid=invalid,
            new=new
        ), retry_inputs

    def has_not_closed_code_blocks(self, text):
        lines = text.split("\n")
        code_block_count = 0  # Counting the number of code block markers (```)

        for index, line in enumerate(lines):
            if "```" in line:
                code_block_count += 1

        if code_block_count % 2 == 1:
            return True

        return False

    def generate(self, messages: List[Message], callback: BaseCallbackHandler = None) -> (str, Stats):
        sys_prompt = ""
        if self.role_prompt:
            sys_prompt += self.role_prompt + "\n"
        else:
            sys_prompt += ROLE_PROMPT + "\n"

        sys_prompt += self.sys_prompt

        if self.few_shot_prompt:
            sys_prompt += "\n" + self.llm.messages_to_prompt(messages=FEW_SHOTS_PYTHON, few_shot_example=True)
        return self.llm.generate(sys_prompt, messages, callback=callback)
