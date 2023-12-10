import logging

from pydantic import BaseModel, Field

from ghostcoder import FileRepository
from ghostcoder.tools.base import Tool, tool, BaseResponse, function

logger = logging.getLogger(__name__)

class UpdateScriptRequest(BaseModel):
    file_path: str = Field(description="Path to the file to write")
    code: str = Field(description="Python code to run to update the file")


class UpdateScriptResponse(BaseResponse):
    file_path: str = Field(description="Path to the file to write")
    git_diff: str = Field(default=None, description="Diff of the file")
    content_after_update: str = Field(default=None, description="Contents of the file after update")
    branch_name: str = Field(default=None, description="Name of the branch")


@tool(name="code_runner")
class CodeRunner(Tool):

    def __init__(self,
                 repository: FileRepository):
        super().__init__()
        self.repository = repository

    @function(
        name="update_script",
        description="Write a script to update a file.",
        request_model=UpdateScriptRequest,
        response_model=UpdateScriptResponse
    )
    def update_script(self, request: UpdateScriptRequest) -> UpdateScriptResponse:
        logger.info(f"Write code to file path {request.file_path}. \n```\n{request.contents}\n```")

        file = self.repository.get_file(request.file_path)
        if not file:
            return UpdateScriptResponse(success=False, error=f"File {request.file_path} not found.")

        return UpdateScriptResponse(
            success=True,
            file_path=request.file_path
        )
