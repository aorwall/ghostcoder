import json
import logging
from typing import List

from openai import OpenAI

from ghostcoder.display_callback import DisplayCallback
from ghostcoder.runtime.base import ChatRuntime
from ghostcoder.schema import Message, Item, TextItem, FunctionItem
from ghostcoder.tools.project_info import ProjectInfo, ProjectInfoRequest
from ghostcoder.utils import count_tokens

logger = logging.getLogger(__name__)


class OpenAIChat(ChatRuntime):

    def __init__(self,
                 model_name: str = "gpt-4-1106-preview",
                 stream: bool = False,
                 max_tokens: int = 16000,
                 **kwargs):
        super().__init__(**kwargs)

        self.model_name = model_name
        self.client = OpenAI()
        self.stream = stream
        self.max_tokens = max_tokens

        self.message_history = []
        self.project_info = ProjectInfo(repository=self.repository, debug_mode=self.debug_mode)

        self.system_prompt = """You're a helpful senior programmer helping a person to understand and write code.
         
You have access to a repository with code. 

Answer questions, show code and write code when needed. 

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
        logger.debug(f"send(): {content}")

        message = Message(role="user", items=[TextItem(text=content)])

        self.message_history.append(message)
        if len(self.message_history) == 1:
            self.message_history.append(self._context_message())

        messages = [{"role": "system", "content": self.system_prompt}]
        tool_id = 0
        for message in self.message_history:
            for item in message.items:
                if isinstance(item, TextItem):
                    logger.debug(f"Text message from {message.role} with {count_tokens(item.text)} tokens.")
                    messages.append({"role": message.role, "content": item.text})
                if isinstance(item, FunctionItem):
                    tool_id += 1
                    argument_str = json.dumps(item.arguments)
                    output_str = json.dumps(item.output)
                    logger.debug(f"Function call {tool_id} to {item.name} with {count_tokens(argument_str)} argument tokens and {count_tokens(output_str)} output tokens.")
                    messages.append({"role": "assistant", "tool_calls": [{"id": f"call_{tool_id}", "function": {"arguments": argument_str, "name": item.name}, "type": "function"}]})
                    messages.append({"role": "tool", "tool_call_id": f"call_{tool_id}", "name": item.name, "content": output_str})

        response_items = self._run(messages)

        response_message = Message(role="assistant", items=response_items)
        self.message_history.append(response_message)
        return response_message

    def _run(self, messages: List, callback: DisplayCallback = None) -> List[Item]:
        response_items = []

        tokens = self._count_tokens(messages)
        if tokens > self.max_tokens and len(messages) > 2:
            logger.debug(f"Reached max tokens ({self.max_tokens}) with {tokens} tokens will remove the oldest of the "
                         f"{len(messages)} messages in context to make context smaller.")
            while tokens > self.max_tokens:
                # For tool messages both the tool request and response must be removed
                if len(messages) > 2 and messages[2].role == "tool":
                    messages.pop(1)
                messages.pop(1)
                tokens = self._count_tokens(messages)

        logger.debug(f"_run() with {len(messages)} messages with {tokens} tokens.")

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            tools=self._function_schemas,
            stream=self.stream,
            tool_choice="auto",
        )
        response_message = response.choices[0].message

        if response_message.content:
            logger.debug(f"response_message.content: {response_message.content}")
            text_item = TextItem(text=response_message.content)
            response_items.append(text_item)
            if callback:
                callback.on_new_item(text_item)

        tool_calls = response_message.tool_calls
        if tool_calls:
            messages.append(response_message)
            logger.debug(f"{len(tool_calls)} tool calls.")

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                logger.debug(f"tool_call function_name: {function_name}, function_args={function_args}")

                function_response = self.run_function(function_name, function_args)
                logger.debug(f"function_response tokens: {count_tokens(str(function_response.json()))}")
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response.json(),
                    }
                )

                function_item = FunctionItem(name=function_name, arguments=function_args, output=function_response.dict())
                response_items.append(function_item)
                if callback:
                    callback.on_new_item(function_item)

            response_items.extend(self._run(messages))

        return response_items

    def _context_message(self):
        project_info = self.run_function("project_info", {})
        function_item = FunctionItem(name="project_info", arguments={}, output=project_info.dict())
        return Message(role="assistant", items=[function_item])


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

    chat = OpenAIChat(repo_dir="/home/albert/repos/p24/playground/rtcstats-server", debug_mode=True)

    print(chat.send("Explain process.js"))