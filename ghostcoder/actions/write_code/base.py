import difflib
import logging
import re
from typing import List, Union, Tuple
from typing import Optional

from pydantic import BaseModel, Field

from codeblocks import create_parser, CodeBlockType
from ghostcoder.actions.base import BaseAction
from ghostcoder.actions.write_code.prompt import get_implement_prompt, FEW_SHOT_PYTHON_1, ROLE_PROMPT, FEW_SHOTS_PYTHON
from ghostcoder.filerepository import FileRepository
from ghostcoder.llm.base import LLMWrapper
from ghostcoder.schema import Message, FileItem, Stats, TextItem, UpdatedFileItem, CodeItem
from ghostcoder.utils import is_complete
from ghostcoder.verify.verifier import Verifier

logger = logging.getLogger(__name__)

class FileBlock(BaseModel):
    file_path: str = Field(description="Path to the file")
    language: str = Field(default=None, description="The language of the code")
    content: str = Field(default="", description="The full updated content.")


class CodeBlock(BaseModel):
    content: str = Field(description="The updated content.")
    language: str = Field(default=None, description="The language of the code")


def get_file_item(items: list, file_path: str):
    for item in items:
        if isinstance(item, FileItem) and item.file_path == file_path:
            return item
        if isinstance(item, UpdatedFileItem) and item.file_path == file_path:
            return item
    return None


def extract_response_parts(response: str) -> List[Union[str, FileBlock]]:
    """
    This function takes a string containing text and code blocks.
    It returns a list of CodeBlock, FileBlock, and non-code text in the order they appear.

    The function can parse two types of code blocks:

    1) Square-bracketed code blocks with optional Filepath:
    Filepath: /path/to/file
    [LANGUAGE]
    code here
    [/LANGUAGE]

    2) Backtick code blocks with optional Filepath:
    Filepath: /path/to/file
    ```LANGUAGE
    code here
    ```

    Parameters:
    text (str): The input string containing code blocks and text

    Returns:
    list: A list containing instances of CodeBlock, FileBlock, and non-code text strings.
    """

    combined_parts = []

    crlf_count = response.count('\r\n')
    if crlf_count > 0:
        logger.info(f"Found {crlf_count} CRLF line breaks in response, replacing with LF")
        response = response.replace('\r\n', '\n').replace('\r', '\n')

    pattern = re.compile(r'(Filepath:\s*(.*?)\n)?\[(.*?)\]\n(.*?)\n\[/\3\]|(Filepath:\s*(.*?)\n)?```(\w+)?\n(.*?)\n```', re.DOTALL)

    last_end = 0

    for match in pattern.finditer(response):
        start, end = match.span()

        non_code_text = response[last_end:start].strip()
        if non_code_text:
            combined_parts.append(non_code_text)

        # For square-bracketed code blocks
        if match.group(3):
            file_path = match.group(2)
            file_path = file_path.strip() if file_path else None
            language = match.group(3).lower()
            content = match.group(4).strip()
            if file_path:
                code_block = FileBlock(file_path=file_path, language=language, content=content)
            else:
                code_block = CodeBlock(language=language, content=content)
            combined_parts.append(code_block)

        # For backtick code blocks
        else:
            file_path = match.group(6)
            file_path = file_path.strip() if file_path else None
            language = match.group(7)
            content = match.group(8).strip()
            if file_path:
                code_block = FileBlock(file_path=file_path, language=language, content=content)
            else:
                code_block = CodeBlock(language=language, content=content)
            combined_parts.append(code_block)

        last_end = end

    # Capture any remaining non-code text
    remaining_text = response[last_end:].strip()
    if remaining_text:
        combined_parts.append(remaining_text)

    return combined_parts


def do_diff(file_path: str, original_content: str, updated_content: str) -> Optional[str]:
    return "".join(difflib.unified_diff(
        original_content.strip().splitlines(True),
        updated_content.strip().splitlines(True),
        fromfile=file_path, tofile=file_path, lineterm='\n'))


class WriteCodeAction(BaseAction):

    def __init__(self,
                 llm: LLMWrapper,
                 role_prompt: Optional[str] = None,
                 sys_prompt_id: Optional[str] = None,
                 sys_prompt: Optional[str] = None,
                 repository: FileRepository = None,
                 auto_mode: bool = False,
                 few_shot_prompt: bool = False,
                 tries: int = 2,
                 verifier: Optional[Verifier] = None):
        if not sys_prompt:
            sys_prompt = get_implement_prompt(sys_prompt_id)
        super().__init__(llm, sys_prompt)
        self.llm = llm
        self.repository = repository
        self.auto_mode = auto_mode
        self.tries = tries
        self.role_prompt = role_prompt
        self.few_shot_prompt = few_shot_prompt
        self.verifier = verifier

    def execute(self, message: Message, message_history: List[Message] = []) -> List[Message]:
        file_items = message.find_items_by_type(item_type="file")
        for file_item in file_items:
            if not file_item.content and self.repository:
                logger.debug(f"Get current file content for {file_item.file_path}")
                content = self.repository.get_file_content(file_path=file_item.file_path)
                if content:
                    file_item.content = content
                else:
                    logger.debug(f"Could not find file {file_item.file_path} in repository, "
                                 f"will assume it's a request to create a new file")
                    file_item.content = ""

        ai_messages = self._execute(messages=[message], message_history=message_history, retry=0)
        stats = [msg.stats for msg in ai_messages if msg.stats]
        use_log = ""
        if stats:
            total_usage = sum(stats[1:], stats[0])
            use_log = f"Used {total_usage.prompt_tokens} prompt tokens, {total_usage.prompt_tokens}. "
            if total_usage.total_cost:
                use_log += f"Total cost: {total_usage.total_cost}. "

        logger.info(f"Finished executing with {len(ai_messages)} messages. {use_log}")

        return ai_messages

    def _execute(self, messages: [Message], message_history: List[Message] = None, retry: int = 0) -> List[Message]:
        file_items = []
        for message in messages:
            file_items_in_message = message.find_items_by_type(item_type="file")
            file_items.extend(file_items_in_message)

        if file_items:
            incoming_files = ""
            for file_item in file_items:
                incoming_files += f"\n- {file_item.to_log()}"
            logger.info(f"Incoming files:{incoming_files}")
        else:
            logger.info(f"No incoming files")

        result, stats = self.generate(messages=messages, history=message_history)
        blocks = extract_response_parts(result)

        retry_inputs = []

        items = []
        for block in blocks:
            if isinstance(block, CodeBlock):
                logger.debug("Received code block: [{}...]".format(block.content[:25].replace("\n", "\\n")))
                stats.increment("code_block")
                file_block = self.code_to_file_block(block, file_items, stats)
                if file_block:
                    block = file_block
                else:
                    items.append(CodeItem(language=block.language, content=block.content))
                    continue

            if isinstance(block, FileBlock):
                updated_file_item, retry_inputs_for_file = self.updated_file(stats, block, file_items)
                if updated_file_item:
                    items.append(updated_file_item)
            else:
                logger.debug("Received text block: [{}...]".format(block[:25].replace("\n", "\\n")))
                items.append(TextItem(text=block))
                if self.has_not_closed_code_blocks(block):
                    stats.increment("not_closed_code_block")
                    retry_inputs.append(
                        TextItem(text="You responded with a incomplete code block. "
                                      "Please provide the contents of the whole file in a code block closed with ```."))

        outgoing_files = ""

        did_changes = False
        for item in items:
            if item.type == "updated_file":
                if not item.invalid and self.repository:
                    try:
                        diff = self.repository.update_file(item.file_path, item.content)
                        did_changes = bool(diff)
                        if not did_changes:
                            item.invalid = "no_change"
                    except Exception as e:
                        item.error = f"Failed to update file {item.file_path}: {e}"
                        stats.increment("failed_to_update_file")
                        logger.error(item.error)
                outgoing_files += f"\n- {item.to_log()}"

        if outgoing_files:
            logger.info(f"Outgoing files: {outgoing_files}")
        else:
            logger.info(f"No outgoing files")

        ai_message = Message(sender="AI", items=items, stats=stats)
        ai_messages = [ai_message]

        if self.auto_mode and self.verifier and did_changes:
            verification_result = self.verifier.verify()
            if not verification_result.success:
                retry_input = TextItem(text=verification_result.message)
                retry_message = Message(
                    sender="Human",
                    items=[retry_input] + verification_result.failures,
                    auto=True
                )
                ai_messages.append(retry_message)
                if retry < self.tries:
                    logger.info(f"Retrying execution (try: {retry}/{self.tries})")
                    ai_messages.extend(self._execute(messages=messages + ai_messages, message_history=message_history, retry=retry + 1))

        if self.auto_mode and retry_inputs:
            retry += 1
            retry_message = Message(sender="Human", items=retry_inputs, auto=True)
            logger.info(f"Found invalid input in the response.\n {retry_message.to_prompt()}")
            ai_messages.append(retry_message)
            if retry < self.tries:
                logger.info(f"Retrying execution (try: {retry}/{self.tries})")
                ai_messages.extend(self._execute(messages=messages + ai_messages, message_history=message_history, retry=retry + 1))

        return ai_messages

    def code_to_file_block(self, block: CodeBlock, file_items: List[FileItem], stats: Stats) -> Optional[FileBlock]:
        """Tries to find a file item that matches the code block."""

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
                    return FileBlock(
                        file_path=file_item.file_path,
                        content=block.content,
                        language=file_item.language)
            except Exception as e:
                logger.warning(
                    f"Could not parse file with {file_item.language} or code block with language {block.language}: {e}")

        return None

    def updated_file(self, stats: Stats, block: FileBlock, file_items: List[FileItem]) -> Tuple[Optional[UpdatedFileItem], List[TextItem]]:
        logger.debug("Received file block: [{}]".format(block.file_path))
        stats.increment("file_item")
        original_file_item = get_file_item(file_items, block.file_path)

        retry_inputs = []

        warning = None
        updated_content = block.content
        invalid = None
        new = False

        if original_file_item and original_file_item.readonly:
            return UpdatedFileItem(
                file_path=block.file_path,
                content=updated_content,
                invalid="readonly",
            ), retry_inputs

        parser = None
        if block.language:
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
                        FileItem(language=block.language, content=error_block.to_string(), file_path=block.file_path))
            elif original_file_item and not original_file_item.readonly:
                original_block = parser.parse(original_file_item.content)
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

        if original_file_item:
            diff = do_diff(file_path=block.file_path, original_content=original_file_item.content,
                           updated_content=updated_content)
            if not diff:
                invalid = "no_change"
                stats.increment("no_change")

            if original_file_item.readonly:
                invalid = "readonly"
                stats.increment("updated_readonly_file")

            if not invalid:
                original_file_item.content = updated_content
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

    def generate(self, messages: List[Message], history: List[Message] = []) -> (str, Stats):
        sys_prompt = ""
        if self.role_prompt:
            sys_prompt += self.role_prompt + "\n"
        else:
            sys_prompt += ROLE_PROMPT + "\n"

        sys_prompt += self.sys_prompt

        if self.few_shot_prompt:
            sys_prompt += "\n" + self.llm.messages_to_prompt(messages=FEW_SHOTS_PYTHON, few_shot_example=True)
        return self.llm.generate(sys_prompt, history + messages)
