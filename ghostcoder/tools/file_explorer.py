import logging
from typing import Optional, List

from pydantic import Field, BaseModel

from ghostcoder import FileRepository
from ghostcoder.codeblocks import create_parser, CodeBlockType
from ghostcoder.index.code_index import CodeIndex
from ghostcoder.schema import FileItem, File
from ghostcoder.tools.base import function, Tool, BaseResponse

logger = logging.getLogger(__name__)

class FindFilesRequest(BaseModel):
    description: Optional[str] = Field(default=None, description="Detailed description of the files to find")
    language: Optional[str] = Field(default=None, description="Programming language of the files to find", enum=["javascript", "python", "java", "typescript"])
    file_extension: Optional[str] = Field(default=None, description="File extension of the files to find")
    directory: Optional[str] = Field(default=None, description="Path to the directory to find files in.")
    names: List[str] = Field(default=None, description="List of file names to find")
    purpose: Optional[str] = Field(default="any", description="Purpose of the files to find", enum=["test", "code", "any"])

class FindFilesResponse(BaseResponse):
    files: List[FileItem]

class ReadFileRequest(BaseModel):
    file_path: str = Field(description="Path to the file to read")

class ReadFileResponse(BaseResponse):
    file_path: str
    contents: Optional[str] = None

class FileExplorer(Tool):

    def __init__(self, repository: FileRepository, code_index: CodeIndex = None, debug_mode: bool = False):
        super().__init__()
        self.repository = repository
        self.code_index = code_index
        self.debug_mode = debug_mode

    @function(
        name="find_files",
        description="Find files.",
        request_model=FindFilesRequest,
        response_model=FindFilesResponse
    )
    def find_files(self, request: FindFilesRequest) -> FindFilesResponse:
        file_tree = self.repository.file_tree(directory=request.directory, file_suffix=request.file_extension)
        files = file_tree.traverse()

        if not files:
            logger.info(f"No files found.")
            return FindFilesResponse(files=[])

        if request.purpose != "any":
            files = [file for file in files if file.purpose == request.purpose]

        if request.language in ["javascript", "python", "java", "typescript"]:
            files = [file for file in files if file.language == request.language]

        if not files:
            logger.info(f"No files found with purpose {request.purpose} and language {request.language}.")
            return FindFilesResponse(files=[])

        if len(files) > 25:
            if self.code_index:
                logger.debug(f"Found {len(files)} files. Will search for relevant files.")

                filter_values = {}
                if request.language:
                    filter_values["language"] = request.language
                if request.purpose != "any":
                    filter_values["purpose"] = request.purpose
                if request.file_extension:
                    filter_values["file_extension"] = request.file_extension

                hits = self.code_index.search(request.description, filter_values=filter_values, limit=25)

                if not hits:
                    logger.debug(f"No hits found. Will return all {len(files)} files.")
                    return FindFilesResponse(files=[FileItem(file_path=file.path) for file in files])

                files = []
                debug_text_before = (f"> _Query: : {request.description}_\n"
                                     f"> _Vector store search hits : {len(hits)}_")
                for i, hit in enumerate(hits):
                    if self.debug_mode:
                        debug_text_before += f"\n> {i + 1}. `{hit.path}` ({len(hit.blocks)} blocks "
                        debug_text_before += ", ".join([f"`{block.identifier}`" for block in hit.blocks])
                        debug_text_before += ")"

                    if any([hit.path in item.path for item in files]):
                        continue

                    # TODO: Add matching blocks to content = self.repository.get_file_content(file_path=hit.path)
                    files.append(File(path=hit.path))

                logging.debug(debug_text_before)

                # TODO: Add other similar files
            else:
                logger.debug(f"Found {len(files)} files. Will return all with no content.")
                return FindFilesResponse(files=[FileItem(file_path=file.path) for file in files])

        file_items = []
        for file in files:
            file_contents = self.repository.get_file_content(file.path)

            if not file_contents:
                logger.info(f"Failed to read file {file.path}")
                continue

            logger.info(f"Found file: {file.path}")
            if file.language:
                try:
                    parser = create_parser(file.language)
                    code_block = parser.parse(file_contents)
                    trimmed_block = code_block.trim_with_types(
                        include_types=[CodeBlockType.FUNCTION, CodeBlockType.CLASS])
                    file_contents = str(trimmed_block)
                except Exception as e:
                    logger.info(f"Failed to parse file {file.path}: {e}")
            else:
                file_contents = file_contents[:500] + " ..."

            file_items.append(FileItem(file_path=file.path, content=file_contents))

        return FindFilesResponse(files=file_items)

    @function(
        name="read_file",
        description="Read file.",
        request_model=ReadFileRequest,
        response_model=ReadFileResponse
    )
    def read_file(self, request: ReadFileRequest) -> ReadFileResponse:
        file_contents = self.repository.get_file_content(file_path=request.file_path)

        if not file_contents:
            logger.info(f"Failed to read file {request.file_path}")
            return ReadFileResponse(success=False, file_path=request.file_path, error=f"File not found.")

        return ReadFileResponse(file_path=request.file_path, contents=file_contents)

