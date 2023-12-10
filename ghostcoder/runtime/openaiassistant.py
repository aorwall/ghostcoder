import json
import logging
from asyncio import sleep
from typing import List

from openai import OpenAI
from openai.types.beta.threads.run_submit_tool_outputs_params import ToolOutput

from ghostcoder.display_callback import DisplayCallback
from ghostcoder.runtime.base import ChatRuntime
from ghostcoder.schema import Message, Item, TextItem, FunctionItem
from ghostcoder.tools.project_info import ProjectInfo, ProjectInfoRequest
from ghostcoder.utils import count_tokens

logger = logging.getLogger(__name__)


class OpenAIAssistantChat(ChatRuntime):

    def __init__(self,
                 model_name: str = "gpt-4-1106-preview",
                 max_tokens: int = 16000,
                 **kwargs):
        super().__init__(**kwargs)

        self.model_name = model_name
        self.client = OpenAI(timeout=30)
        self.thread_id = self.client.beta.threads.create().id
        self.max_tokens = max_tokens

        logger.debug(f"Created thread with ID: {self.thread_id}")
        self.last_message_id = None
        self.assistant_id = "asst_kj5XShFAQNhVRetGXhzoJ91o"

        self.system_prompt = """You're a helpful senior programmer helping a person to understand and write code.
         
You have access to a repository with code. 

Answer questions, show code and write code when needed. 

Always start by using the get_project_info function to get information about the repository you're currently working on. 

ONLY answer questions relevant to the code base you have access to. 
DO NOT answer questions if you don't have the full context. Use functions to get the whole context. 
DO NOT show or suggest hypothetical examples in code that is not in the context.

Use functions to retrieve more information about the code base. 

When you write code, start by suggesting the code change to the user and ask if you should implement the code change. Then create a new branch and use the write_code function to do the change. 

When you update existing code be sure that it can be automatically merged to the existing code base.

If you leave out existing code YOU MUST show this with placeholders like "# ... existing code".   

If you only provide an updated function YOU MUST provide all the code in functions you update.
"""

    def send(self, content: str, callback: DisplayCallback = None) -> Message:
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
                    callback.on_new_items(new_items)

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
        return Message(role="assistant", items=items)

    def get_message_items(self) -> List[TextItem]:
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

    def _count_tokens(self, messages: List):
        content = ""
        for message in messages:
            if isinstance(message, dict):
                content += json.dumps(message)
            else:
                content += message.json()
        return count_tokens(content)


if __name__ == "__main__":
    logging_format = '%(asctime)s -  %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=logging_format)
    logging.getLogger('ghostcoder').setLevel(logging.DEBUG)
    logging.getLogger('__main__').setLevel(logging.DEBUG)
    logging.getLogger('httpx').setLevel(logging.WARNING)

    chat = OpenAIAssistantChat(repo_dir="/home/albert/repos/p24/playground/rtcstats-server", debug_mode=True)

    print(chat.send("Explain process.js"))