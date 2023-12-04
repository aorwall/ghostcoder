import json
import logging
from pathlib import Path

from openai._types import NotGiven

from time import sleep

from openai import OpenAI
from openai.types.beta import thread_create_params
from openai.types.beta.threads.required_action_function_tool_call import Function
from openai.types.beta.threads.run_submit_tool_outputs_params import ToolOutput

from ghostcoder import FileRepository
from ghostcoder.main import Ghostcoder
from ghostcoder.schema import BaseResponse, FunctionItem, Message, TextItem, ListFilesRequest, WriteCodeRequest, \
    CreateBranchRequest

logger = logging.getLogger(__name__)

class Assistant:

    def __init__(self, repo_dir: str = None, debug_mode: bool = False, model_name: str = "gpt-4-1106-preview", ghostcoder: Ghostcoder = None):
        self.ghostcoder = ghostcoder or Ghostcoder(repo_dir=repo_dir, debug_mode=debug_mode, model_name=model_name)
        self.client = OpenAI(timeout=30)
        self.thread_id = self.client.beta.threads.create().id
        logger.debug(f"Created thread with ID: {self.thread_id}")
        self.last_message_id = None
        self.assistant_id = "asst_kj5XShFAQNhVRetGXhzoJ91o"

    def run(self, message: str, callback=None):
        self.client.beta.threads.messages.create(thread_id=self.thread_id, role="user", content=message)
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

                    try:
                        response = self.get_output(tool.function.name, arguments)
                    except Exception as e:
                        logger.warning(f"Failed to run function: {e}")
                        response = BaseResponse(success=False, error=str(e))

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

        if function == "find_files":
            return self.ghostcoder.find_files(**arguments)
        elif function == "list_files":
            return self.ghostcoder.list_files(ListFilesRequest.parse_obj(arguments))
        elif function == "read_file":
            return self.ghostcoder.read_file(**arguments)
        elif function == "write_code":
            return self.ghostcoder.write_code(WriteCodeRequest.parse_obj(arguments))
        elif function == "create_branch":
            return self.ghostcoder.create_branch(CreateBranchRequest.parse_obj(arguments))
        else:
            return BaseResponse(success=False, error=f"Unknown function: {function}")

    def get_message_items(self):
        items = []
        threads_messages = self.client.beta.threads.messages.list(thread_id=self.thread_id, order="asc", after=self.last_message_id)
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

    repository = FileRepository(repo_path=Path("/home/albert/repos/albert/ghostcoder"), exclude_dirs=["benchmark", "playground", "tests"])
    ghostcoder = Ghostcoder(repository=repository, debug_mode=True)
    assistant = Assistant(ghostcoder=ghostcoder, debug_mode=True)
    msg = "Create an OpenAPI spec in JSON for my api"
    while True:
        assistant.run(msg)
        msg = input("User: ")
