import json
import logging
from pathlib import Path

from openai._types import NotGiven

from time import sleep

from openai import OpenAI
from openai.types import FunctionDefinition
from openai.types.beta import thread_create_params
from openai.types.beta.assistant import ToolFunction
from openai.types.beta.threads.required_action_function_tool_call import Function
from openai.types.beta.threads.run_submit_tool_outputs_params import ToolOutput

from ghostcoder import FileRepository
from ghostcoder.display_callback import DisplayCallback
from ghostcoder.main import Ghostcoder
from ghostcoder.schema import BaseResponse, FunctionItem, Message, TextItem, ListFilesRequest, WriteCodeRequest, \
    CreateBranchRequest, FindFilesRequest, ReadFileRequest, ProjectInfoRequest

logger = logging.getLogger(__name__)


class Assistant:

    def __init__(self, repo_dir: str = None, debug_mode: bool = False, model_name: str = "gpt-4-1106-preview",
                 ghostcoder: Ghostcoder = None):
        self.ghostcoder = ghostcoder or Ghostcoder(repo_dir=repo_dir, debug_mode=debug_mode, model_name=model_name)
        self.client = OpenAI(timeout=30)
        self.thread_id = self.client.beta.threads.create().id
        logger.debug(f"Created thread with ID: {self.thread_id}")
        self.last_message_id = None
        self.assistant_id = "asst_kj5XShFAQNhVRetGXhzoJ91o"

    def setup_assistant(self):
        assistant = self.client.beta.assistants.retrieve(assistant_id=self.assistant_id)
        print(assistant)
        Assistant(description=None,
                  instructions="You're a helpful senior programmer helping a person to understand and write code. You have access to a repository with code. \n\nAlways start by using the list_files function to get information about the repository you're currently working on. \n\nAnswer questions and write code when needed. \n\nDO NOT answer questions if you don't have the full context. \nDO NOT show or suggest hypothetical examples in code that is not in the context.\nYou can use the find_files function to find relevant files. Be explicit when you describe what files you search for. \n\nUse functions to retrieve more information about the code base. \n\nIf you're sure about how to do a change you can create a new branch and use the write_code function to do the change.\n\nRemember that you must provide all the code in functions you update. ",
                  metadata={},
                  model='gpt-4-1106-preview',
                  name='Ghostcoder',
                  object='assistant',
                  tools=[
                      ToolFunction(function=FunctionDefinition(name='write_code', parameters={'type': 'object', 'properties': {
                    'contents': {'type': 'string',
                                 'description': 'The code to create or update. Functions must be fully implemented without placeholders. '},
                    'file_path': {'type': 'string', 'description': 'Full path to the file'},
                    'new_file': {'type': 'boolean', 'description': 'If the file is new and should be created'}},
                                                                           'required': ['code', 'file_path']},
                                            description='Write new code or update code in the code base.'),
                    type='function'),
                         ToolFunction(function=FunctionDefinition(name='find_files',
                                                                           parameters={'type': 'object', 'properties': {
                                                                               'description': {'type': 'string',
                                                                                               'description': "A detailed description of the files you're searching for."}},
                                                                                       'required': ['description']},
                                                                           description='Search and find relevant files in the code base by providing a description.'),
                                               type='function'),
                      ToolFunction(
                function=FunctionDefinition(name='read_file', parameters={'type': 'object', 'properties': {
                    'file_path': {'type': 'string', 'description': 'Full file path to the file.'}},
                                                                          'required': ['file_path']},
                                            description='Read a file'), type='function'),
                      ToolFunction(function=FunctionDefinition(name='create_branch', parameters={'type': 'object', 'properties': {
                    'name': {'type': 'string', 'description': 'The name of the branch '}}, 'required': ['name']},
                                            description='Create and checkout a new branch.'), type='function')])

    def send(self, content: str, callback: DisplayCallback=None):
        self.client.beta.threads.messages.create(thread_id=self.thread_id, role="user", content=content)
        run = self.client.beta.threads.runs.create(thread_id=self.thread_id, assistant_id=self.assistant_id)

        items = []

        while True:
            run = self.client.beta.threads.runs.retrieve(run_id=run.id, thread_id=self.thread_id)
            logger.info(f"Run status: {run.status}")

            if run.status in ["completed", "failed"]:
                break
            elif run.status == "requires_action":
                new_items = self.get_message_items()
                if callback:
                    callback.on_new_item(new_items)

                items.extend(new_items)

                logger.info(f"Required action: {run.required_action.type}")
                logger.info(run.required_action.submit_tool_outputs)

                tool_outputs = []

                for tool in run.required_action.submit_tool_outputs.tool_calls:
                    if tool.function.arguments:
                        arguments = json.loads(tool.function.arguments)
                    else:
                        arguments = {}

                    response = self.run_function(tool.function.name, arguments)

                    tool_outputs.append(ToolOutput(tool_call_id=tool.id, output=response.json()))
                    items.append(FunctionItem(function=tool.function.name, arguments=arguments, output=response.dict()))

                run = self.client.beta.threads.runs.submit_tool_outputs(
                    run_id=run.id, thread_id=run.thread_id, tool_outputs=tool_outputs)

                logger.info(f"Submitted tool output. Status: {run.status}")

            sleep(1)

        new_items = self.get_message_items()
        items.extend(new_items)
        return Message(sender="ai", items=items)

    def get_output(self, function: str, arguments: dict) -> BaseResponse:
        logger.info(f"Run function [{function}] with arguments [{arguments}]")

        if function == "get_project_info":
            return self.ghostcoder.get_project_info(ProjectInfoRequest.parse_obj(arguments))
        elif function == "find_files":
            return self.ghostcoder.find_files(FindFilesRequest.parse_obj(arguments))
        elif function == "read_file":
            return self.ghostcoder.read_file(ReadFileRequest.parse_obj(arguments))
        elif function == "write_code":
            return self.ghostcoder.write_code(WriteCodeRequest.parse_obj(arguments))
        elif function == "create_branch":
            return self.ghostcoder.create_branch(CreateBranchRequest.parse_obj(arguments))
        else:
            return BaseResponse(success=False, error=f"Unknown function: {function}")

    def get_message_items(self):
        items = []
        threads_messages = self.client.beta.threads.messages.list(thread_id=self.thread_id, order="asc",
                                                                  after=self.last_message_id)
        logger.info(f"Got {len(threads_messages.data)} messages")
        if threads_messages and threads_messages.data:
            for threads_message in threads_messages.data:
                if threads_message.role == "assistant":
                    for content in threads_message.content:
                        if content.text:
                            logger.info(f"New message:\n{content.text.value}")
                            items.append(TextItem(text=content.text.value))

            self.last_message_id = threads_messages.data[-1].id
        return items


if __name__ == "__main__":
    logging_format = '%(asctime)s - %(name)s  - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=logging_format)
    logging.getLogger('ghostcoder').setLevel(logging.DEBUG)
    logging.getLogger('httpx').setLevel(logging.INFO)
    logging.getLogger('openai').setLevel(logging.INFO)
    logging.getLogger('httpcore').setLevel(logging.INFO)

    repository = FileRepository(repo_path=Path("/home/albert/repos/albert/ghostcoder"),
                                exclude_dirs=["benchmark", "playground", "tests"])
    ghostcoder = Ghostcoder(repository=repository, debug_mode=True)
    assistant = Assistant(ghostcoder=ghostcoder, debug_mode=True)
    assistant.setup_assistant()
    # msg = "Create an OpenAPI spec in JSON for my api"
    # while True:
    #    assistant.run(msg)
    #    msg = input("User: ")
