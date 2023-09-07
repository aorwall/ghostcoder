import difflib
import logging
import re
from pathlib import Path
from typing import List, Union
from typing import Optional

from pydantic import BaseModel, Field

from codeblocks import create_parser, CodeBlockType
from ghostcoder.actions.base import BaseAction
from ghostcoder.actions.write_code.prompt import get_implement_prompt, FEW_SHOT_PYTHON_1, ROLE_PROMPT, FEW_SHOTS_PYTHON
from ghostcoder.filerepository import FileRepository
from ghostcoder.llm.base import LLMWrapper
from ghostcoder.schema import Message, FileItem, Stats, TextItem, UpdatedFileItem, CodeItem
from ghostcoder.utils import is_complete, language_by_filename


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
        logging.info(f"Found {crlf_count} CRLF line breaks in response, replacing with LF")
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

    def execute(self, message: Message, message_history: List[Message] = []) -> List[Message]:
        logging.info("execute()")
        file_items = message.find_items_by_type(item_type="file")
        for file_item in file_items:
            if not file_item.content and self.repository:
                logging.debug(f"execute() Get current file content for {file_item.file_path}")
                content = self.repository.get_file_content(file_path=file_item.file_path)
                if content:
                    file_item.content = content
                else:
                    logging.debug(f"execute() Could not find file {file_item.file_path} in repository, "
                                 f"will assume it's a request to create a new file")
                    file_item.content = ""

        return self._execute(messages=[message], message_history=message_history, retry=0)

    def _execute(self, messages: [Message], message_history: List[Message] = None, retry: int = 0) -> List[Message]:
        result, stats = self.generate(messages=messages, history=message_history)
        blocks = extract_response_parts(result)

        retry_inputs = []

        file_items = []
        for message in messages:
            file_items.extend([item for item in message.items if isinstance(item, FileItem)])

        items = []
        for block in blocks:
            if isinstance(block, CodeBlock):
                logging.debug("execute() Received code block: [{}...]".format(block.content[:25].replace("\n", "\\n")))
                stats.increment("code_block")
                file_block = self.code_to_file_block(block, file_items, stats)
                if file_block:
                    block = file_block
                else:
                    items.append(CodeItem(language=block.language, content=block.content))
                    continue

            if isinstance(block, FileBlock):
                logging.debug("execute() Received file block: [{}]".format(block.file_path))
                stats.increment("file_item")
                original_file_item = get_file_item(file_items, block.file_path)

                warning = None
                updated_content = block.content
                invalid = False

                parser = None
                if block.language:
                    try:
                        parser = create_parser(block.language)
                    except Exception as e:
                        logging.warning(f"execute() Could not create parser for language {block.language}: {e}")

                if parser:
                    try:
                        updated_block = parser.parse(updated_content)
                    except Exception as e:
                        logging.warning(f"execute() Could not parse updated  in {block.file_path}: {e}")
                        stats.increment("invalid_code_block")
                        retry_input = f"You returned a file with the following invalid code blocks: \n" + updated_content
                        retry_inputs.append(TextItem(text=retry_input))
                        continue

                    error_blocks = updated_block.find_errors()
                    if error_blocks:
                        stats.increment("files_with_errors")
                        logging.info("execute() The updated file {} has errors. ".format(block.file_path))
                        retry_inputs.append(TextItem(text="You returned a file with syntax errors. Find them and correct them."))
                        invalid = True
                        for error_block in error_blocks:
                            retry_inputs.append(FileItem(language=block.language, content=error_block.to_string(), file_path=block.file_path))
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
                            logging.info("execute() The merged file {} has errors..".format(block.file_path))
                            retry_inputs.append(TextItem(text="You returned a file with syntax errors. Find them and correct them."))
                            invalid = True
                            for error_block in error_blocks:
                                retry_inputs.append(FileItem(language=block.language, content=error_block.to_string(), file_path=block.file_path))

                if not retry_inputs and not is_complete(updated_content):
                    logging.info(f"execute() The content in block [{block.file_path}] is not complete, will retry")
                    stats.increment("not_complete_file")
                    retry_inputs.append(TextItem(text=f"Return all code from the original code in the update file {block.file_path}."))
                    invalid = True

                if original_file_item:
                    diff = do_diff(file_path=block.file_path, original_content=original_file_item.content, updated_content=updated_content)
                    if not diff:
                        invalid = True
                        stats.increment("no_change")

                    if original_file_item.readonly:
                        invalid = True
                        stats.increment("updated_readonly_file")

                    if not invalid:
                        original_file_item.content = updated_content
                elif self.repository.get_file_content(block.file_path):
                    # TODO: Check in context if the file might exist in earlier messages
                    logging.info(f"execute() {block.file_path} not found in initial message but exists in repo, will assume"
                                 f"that it's a hallucination and ignore the file.")
                    stats.increment("hallucinated_file")
                    continue
                else:
                    stats.increment("new_file")
                    logging.debug(f"execute() {block.file_path} not found in initial message, assume new file.")

                items.append(UpdatedFileItem(
                    file_path=block.file_path,
                    content=updated_content,
                    error=warning,
                    invalid=invalid
                ))
            else:
                logging.debug("execute() Received text block: [{}...]".format(block[:25].replace("\n", "\\n")))
                items.append(TextItem(text=block))
                if self.has_not_closed_code_blocks(block):
                    stats.increment("not_closed_code_block")
                    retry_inputs.append(
                        TextItem(text="You responded with a incomplete code block. "
                                      "Please provide the contents of the whole file in a code block closed with ```."))

        for item in items:
            if item.type == "updated_file" and not item.invalid and self.repository:
                try:
                    self.repository.update_file(item.file_path, item.content)
                except Exception as e:
                    item.error = f"Failed to update file {item.file_path}: {e}"
                    stats.increment("failed_to_update_file")
                    logging.error(item.error)

        ai_messages = [Message(
            sender="AI",
            items=items,
            usage=[stats]
        )]

        if self.auto_mode and retry_inputs and retry < self.tries:
            retry_message = Message(
                sender="Human",
                items=retry_inputs
            )
            ai_messages.append(retry_message)
            ai_messages.extend(self._execute(messages=messages + ai_messages, message_history=message_history, retry=retry + 1))

        return ai_messages

    def code_to_file_block(self, block: CodeBlock, file_items: List[FileItem], stats: Stats) -> Optional[FileBlock]:
        """Tries to find a file item that matches the code block."""

        for file_item in file_items:
            if not file_item.language:
                continue

            if block.language and block.language != file_item.language:
                logging.debug(
                    f"execute() Language in block [{block.language}] does not match language [{file_item.language}] file path {file_item.file_path}")
                continue

            try:
                parser = create_parser(file_item.language)
                original_block = parser.parse(file_item.content)
                updated_block = parser.parse(block.content)

                matching_blocks = original_block.get_matching_blocks(updated_block)
                if any(matching_block for matching_block in matching_blocks
                       if matching_block.type in [CodeBlockType.FUNCTION, CodeBlockType.CLASS]):
                    matching_content_str = "".join([f"\n- {block.content.strip()}" for block in matching_blocks])
                    logging.info(f"execute() Code block has similarities to {file_item.file_path}, will assume it's the "
                                 f"updated file.\nSimilarities:{matching_content_str})")
                    stats.increment("guess_file_item")
                    return FileBlock(
                        file_path=file_item.file_path,
                        content=block.content,
                        language=file_item.language)
            except Exception as e:
                logging.warning(
                    f"Could not parse file with {file_item.language} or code block with language {block.language}: {e}")

        return None

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
