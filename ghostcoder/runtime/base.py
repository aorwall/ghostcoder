import logging
from pathlib import Path

from llama_index.vector_stores.types import VectorStore

from ghostcoder import FileRepository
from ghostcoder.display_callback import DisplayCallback
from ghostcoder.index.code_index import CodeIndex
import traceback

from ghostcoder.schema import Message
from ghostcoder.tools.base import BaseResponse
from ghostcoder.tools.code_runner import CodeRunner
from ghostcoder.tools.code_writer import CodeWriter
from ghostcoder.tools.file_explorer import FileExplorer
from ghostcoder.tools.project_info import ProjectInfo

logger = logging.getLogger(__name__)

class Runtime:

    def __init__(self,
                 repository: FileRepository = None,
                 code_index: CodeIndex = None,
                 vector_store: VectorStore = None,
                 callback: DisplayCallback = None,
                 repo_dir: str = None,
                 search_limit: int = 5,
                 debug_mode: bool = False):

        exclude_dirs = [".index", ".prompt_log"]

        self.repository = repository or FileRepository(repo_path=Path(repo_dir), exclude_dirs=exclude_dirs)
        logger.debug(f"Using repository {self.repository}.")
        try:
            self.code_index = code_index or CodeIndex(repository=self.repository,
                                                      vector_store=vector_store,
                                                      limit=search_limit)
        except Exception as e:
            logger.warning(f"Failed to create code index: {e}")
            traceback.print_exc()
            self.code_index = None

        self.callback = callback

        self.debug_mode = debug_mode

        self._tools = []
        self._tools.append(FileExplorer(repository=self.repository, code_index=self.code_index, debug_mode=self.debug_mode))
        self._tools.append(CodeWriter(repository=self.repository, debug_mode=self.debug_mode))
        self._tools.append(ProjectInfo(repository=self.repository, debug_mode=self.debug_mode))
        self._tools.append(CodeRunner(repository=self.repository, debug_mode=self.debug_mode))

        self._tool_by_function = {}
        self._function_schemas = []
        for tool in self._tools:
            for function_name in tool.function_names:
                self._tool_by_function[function_name] = tool

            self._function_schemas.extend(tool.schema)

    def get_tool(self, function_name: str):
        return self._tool_by_function.get(function_name, None)

    def run_function(self, function_name: str, arguments: dict) -> BaseResponse:
        tool = self.get_tool(function_name)
        if not tool:
            return BaseResponse(success=False, error=f"Function {function_name} not found.")

        try:
            return tool.run(function_name, arguments)
        except Exception as e:
            logger.warning(f"Failed to run function: {e}")
            return BaseResponse(success=False, error=str(e))



class ChatRuntime(Runtime):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def send(self, content: str, callback: DisplayCallback = None) -> Message:
        pass
