import logging
from typing import Optional, List, Dict

from pydantic import Field, BaseModel

from ghostcoder import FileRepository
from ghostcoder.schema import FileItem, File, Folder
from ghostcoder.tools.base import function, Tool, BaseResponse

logger = logging.getLogger(__name__)

class ProjectInfoRequest(BaseModel):
    project_name: str = Field(default=None, description="Name of the project, empty if unknown")

class DirectorySummary(BaseModel):
    name: str
    first_files_in_directory: List[str] = []
    files_by_file_type: Dict[str, int] = {}
    children: List["DirectorySummary"] = []

class ProjectInfoResponse(BaseResponse):
    repository: str = Field(description="Name of the repository")
    file_tree: DirectorySummary = Field(default=[], description="Info about the files in the repository")
    relevant_files: List[FileItem] = Field(default=[], description="List of relevant files in the repository")

class ProjectInfo(Tool):

    def __init__(self, repository: FileRepository, debug_mode: bool = False):
        super().__init__()
        self.repository = repository
        self.debug_mode = debug_mode

    @function(
        name="project_info",
        description="Returns the current projects name, directory structure, programming languages used and other essential information.",
        request_model=ProjectInfoRequest,
        response_model=ProjectInfoResponse
    )
    def get_project_info(self, request: ProjectInfoRequest) -> ProjectInfoResponse:
        repo_name = self.repository.repo_path.name
        file_tree_summary = self._create_directory_summary(self.repository.file_tree())

        relevant_files = []
        readme = self.repository.get_file_content("README.md")
        if readme:
            relevant_files.append(FileItem(file_path="README.md", content=readme[0:1000]))

        response = ProjectInfoResponse(
            repository=repo_name,
            file_tree=file_tree_summary,
            relevant_files=relevant_files)

        logger.debug(f"Project info: {response}")

        return response

    def _create_directory_summary(self, folder: Folder):
        first_files_in_directory = [file.path for file in folder.children[:3] if isinstance(file, File)]

        children = []
        number_of_files_by_extension = {}
        for file in folder.children:
            if isinstance(file, File):
                if "." not in file.path:
                    continue
                file_extension = file.path.split(".")[-1]
                number_of_files_by_extension[file_extension] = number_of_files_by_extension.get(file_extension, 0) + 1
            elif isinstance(file, Folder):
                directory_summary = self._create_directory_summary(file)
                children.append(directory_summary)

        return DirectorySummary(
            name=folder.name,
            first_files_in_directory=first_files_in_directory,
            files_by_file_type=number_of_files_by_extension,
            children=children
        )
