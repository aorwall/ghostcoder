import difflib
import logging
from typing import List
from typing import Optional

from pydantic import BaseModel, Field

from ghostcoder import FileRepository
from ghostcoder.codeblocks import create_parser, CodeBlockType
from ghostcoder.display_callback import DisplayCallback
from ghostcoder.schema import FileItem, UpdatedFileItem
from ghostcoder.tools.base import function, Tool, tool, BaseResponse
from ghostcoder.utils import is_complete

logger = logging.getLogger(__name__)


def do_diff(file_path: str, original_content: str, updated_content: str) -> Optional[str]:
    return "".join(difflib.unified_diff(
        original_content.strip().splitlines(True),
        updated_content.strip().splitlines(True),
        fromfile=file_path, tofile=file_path, lineterm="\n"))


class WriteCodeRequest(BaseModel):
    file_path: str = Field(description="Path to the file to write")
    contents: str = Field(description="Contents of the file")
    new_file: bool = Field(default=False, description="If the file is new and doesn't exist in the repository")


class WriteCodeResponse(BaseResponse):
    file_path: str = Field(description="Path to the file to write")
    git_diff: str = Field(default=None, description="Diff of the file")
    content_after_update: str = Field(default=None, description="Contents of the file after update")
    branch_name: str = Field(default=None, description="Name of the branch")


@tool(name="code_writer")
class CodeWriter(Tool):

    def __init__(self,
                 repository: FileRepository,
                 allow_hallucinated_files: bool = False,
                 expect_complete_functions: bool = True,
                 guess_similar_files: bool = True,
                 remove_new_comments: bool = True,
                 debug_mode: bool = False,
                 callback: DisplayCallback = None):
        super().__init__()
        self.repository = repository
        self.guess_similar_files = guess_similar_files
        self.expect_complete_functions = expect_complete_functions
        self.allow_hallucinated_files = allow_hallucinated_files
        self.remove_new_comments = remove_new_comments
        self.debug_mode = debug_mode
        self.callback = callback

    @function(
        name="write_code",
        description="Write new code or update code in the code base.",
        request_model=WriteCodeRequest,
        response_model=WriteCodeResponse,
        is_consequential=True
    )
    def write_code(self, request: WriteCodeRequest) -> WriteCodeResponse:
        logger.info(f"Write code to file path {request.file_path}. \n```\n{request.contents}\n```")

        # TODO: Check if branch is not trunk

        debug_text_before = f"> _Provided files from file context:_"
        for i, file_item in enumerate(self.repository.file_context):
            debug_text_before += f"\n> {i + 1}. `{file_item.file_path}`"

        debug_text_before += "\n\n"

        if self.debug_mode:
            logger.debug(debug_text_before)

        existing_file = self.repository.get_file(request.file_path)
        if request.new_file:
            if existing_file:
                return WriteCodeResponse(success=False,
                                         file_path=request.file_path,
                                         error=f"An existing file found.")

            updated_file = UpdatedFileItem(file_path=request.file_path, content=request.contents)

        else:
            if not existing_file:
                return WriteCodeResponse(success=False,
                                         file_path=request.file_path,
                                         error=f"No existing file found.")

            updated_file = self.update_file(new_updates=request.contents,
                                            file_path=request.file_path,
                                            existing_file_item=existing_file)
            if updated_file.invalid:
                logger.info(f"Updated code is invalid, {updated_file.invalid}")
                return WriteCodeResponse(success=False,
                                         file_path=request.file_path,
                                         content_after_update=updated_file.content,
                                         error=updated_file.invalid)

        logger.info(f"Updated code diff:\n{updated_file.diff}")

        if self.debug_mode:
            debug_text_after = f"\n\n> _Updated file:_\n> {updated_file.file_path}\n```diff\n{updated_file.diff}\n```"
            logger.debug(debug_text_after)

        diff = self.repository.update_file(file_path=updated_file.file_path, content=updated_file.content)
        return WriteCodeResponse(git_diff=diff,
                                 content_after_update=updated_file.content,
                                 file_path=updated_file.file_path,
                                 branch_name=self.repository.active_branch)

    def find_matching_file_item(self,
                                code: str,
                                file_path: str = None,
                                language: str = None,
                                file_items: List[FileItem] = []):
        """Tries to find a file item that matches the code block."""

        if file_path:
            equal_match = [item for item in file_items if "file" in item.type and item.file_path == file_path]
            if equal_match:
                logger.debug(f"Found equal match for {file_path}: {equal_match[0].file_path}")
                return equal_match[0]

            similar_matches = [item for item in file_items if "file" in item.type and file_path in item.file_path]
            if len(similar_matches) == 1:
                logger.debug(f"Found similar match for {file_path}: {similar_matches[0].file_path}")
                return similar_matches[0]
            elif len(similar_matches) > 1:
                logger.debug(
                    f"Found {len(similar_matches)} similar matches for {file_path}: {similar_matches}, expected one")
                file_items = similar_matches

        if not self.guess_similar_files:
            file_names = ", ".join([item.file_path for item in file_items])
            logger.debug(f"Could not find a matching file item for {file_path} in file context with files {file_names}")
            return None

        for file_item in file_items:
            if not file_item.language:
                continue

            if language and language != file_item.language:
                logger.debug(
                    f"Language in block [{language}] does not match language [{file_item.language}] file path {file_item.file_path}")
                continue

            try:
                parser = create_parser(file_item.language)
                original_block = parser.parse(file_item.content)
                updated_block = parser.parse(code)

                # TODO: Sort by matching blocks first and pick the one with the most matching blocks
                matching_blocks = original_block.get_matching_blocks(updated_block)
                if any(matching_block for matching_block in matching_blocks
                       if matching_block.type in [CodeBlockType.FUNCTION, CodeBlockType.CLASS]):
                    matching_content_str = "\n\n".join([str(block) for block in matching_blocks])
                    self.debug_log(
                        f"Code block has similarities to {file_item.file_path}, will assume it's the "
                        f"updated file.\nSimilarities:\n```\n{matching_content_str}\n```")

                    return file_item
            except Exception as e:
                logger.warning(
                    f"Could not parse file with {file_item.language} or code block with language {language}: {e}")

        if (len(file_items) == 1
                and file_items[0].language == language):
            self.debug_log(f"Found only the file {file_items[0].file_path} with language {language}, "
                           f"will assume it's the updated file.")
            return file_items[0]

    def update_file(self,
                    new_updates: str,
                    file_path: str = None,
                    language: str = None,
                    existing_file_item: Optional[FileItem] = None) -> Optional[UpdatedFileItem]:
        logger.debug(f"update_file: file_path={file_path}, language={language}, "
                     f"existing_file_item={existing_file_item is not None}")

        language = language or existing_file_item.language

        updated_content = new_updates

        if not file_path and existing_file_item:
            file_path = existing_file_item.file_path

        def invalid_update(invalid: Optional[str] = None, updated_content: str = None):
            return UpdatedFileItem(
                file_path=file_path,
                language=language,
                content=updated_content,
                new_updates=new_updates,
                invalid=invalid
            )

        # Don't merge and mark as invalid if the file is readonly
        if existing_file_item and existing_file_item.readonly:
            return invalid_update("readonly")

        # Don't merge and mark as invalid if hallucinated files isn't allowed
        if not existing_file_item and not self.allow_hallucinated_files:
            return invalid_update("hallucination")

        parser = None
        try:
            parser = create_parser(language, apply_gpt_tweaks=True)
        except Exception as e:
            logger.warning(f"Could not create parser for language {language}: {e}")

        if parser:
            try:
                updated_block = parser.parse(updated_content)
            except Exception as e:
                logger.warning(f"Could not parse updated in {file_path}: {e}")
                return invalid_update("Couldn't parse the content, please provide valid code.")

            error_blocks = updated_block.find_errors()
            if error_blocks:
                logger.info("The updated file {} has errors. ".format(file_path))
                error_block_report = "\n\n".join([f"```{block.content}```" for block in error_blocks])
                return invalid_update(f"There are syntax errors in the updated file:\n\n{error_block_report}")

            if self.expect_complete_functions:
                incomplete_blocks = updated_block.find_incomplete_blocks_with_types(
                    [CodeBlockType.CONSTRUCTOR, CodeBlockType.FUNCTION, CodeBlockType.TEST_CASE])
                if incomplete_blocks:
                    incomplete_blocks_str = ", ".join([f"`{block.identifier}`" for block in incomplete_blocks])
                    return invalid_update(f"All code must be provided in the functions. "
                                          f"The content in the functions {incomplete_blocks_str} is not complete.")

            if existing_file_item and not existing_file_item.readonly:
                original_block = parser.parse(existing_file_item.content)

                try:
                    original_block.merge(updated_block)

                    updated_content = original_block.to_string()

                    merged_block = parser.parse(updated_content)
                    error_blocks = merged_block.find_errors()
                    if error_blocks:
                        logger.info("The merged file {} has errors.".format(file_path))
                        return invalid_update("Couldn't merge the updated content to the existing file. Please provide the complete contents of the existing file when updating it.", updated_content=updated_content)

                    if not original_block.is_complete():
                        logger.info(f"The merged content for [{file_path}] is not complete")
                        return invalid_update("Couldn't merge the updated content to the existing file. Please provide the complete contents of the existing file when updating it.",  updated_content=updated_content)

                except ValueError as e:
                    logger.info(f"Could not merge {file_path}: {e}")
                    return invalid_update("Couldn't merge the updated content to the existing file. Please provide the complete contents of the existing file when updating it.")
        elif not is_complete(updated_content):
            return invalid_update("No code isn't complete, provide the missing code.")

        diff = None
        if existing_file_item:
            diff = do_diff(file_path=file_path,
                           original_content=existing_file_item.content,
                           updated_content=updated_content)
            if not diff:
                return invalid_update("no_change")

        return UpdatedFileItem(
            file_path=file_path,
            language=language,
            new_updates=new_updates,
            content=updated_content,
            diff=diff)

    def debug_log(self, message):
        if self.callback:
            self.callback.debug(message)
