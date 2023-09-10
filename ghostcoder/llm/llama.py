import time
from typing import List, Any

from langchain.llms.base import create_base_retry_decorator

from ghostcoder.llm.base import LLMWrapper
from ghostcoder.schema import Message, Stats, FileItem


class LlamaLLMWrapper(LLMWrapper):

    def generate(self, sys_prompt: str, messages: List[Message]) -> (str, Stats):
        starttime = time.time()

        prompt_value = "<s>[INST]<<SYS>>\n" + sys_prompt + "\n<</SYS>>\n"
        prompt_value += self.messages_to_prompt(messages)
        prompt_value += "[/INST]"

        # TODO: For testing
        last_file = ""
        for message in messages:
            if message.sender == "Human":
                for item in message.items :
                    if isinstance(item, FileItem):
                        last_file = "\n" + item.file_path + "\n```python\n"

        prompt_value += last_file

        retry_decorator = create_base_retry_decorator(error_types=[ValueError], max_retries=5)

        @retry_decorator
        def _completion_with_retry() -> Any:
            return self.llm.predict(prompt_value)

        result = _completion_with_retry()

        if last_file:
            result = last_file + result + "```"

        usage = Stats.from_dict(
            prompt=self.__class__.__name__,
            llm_output={},
            duration=time.time() - starttime)

        return result, usage

    def messages_to_prompt(self, messages: List[Message], few_shot_example: bool = False):
        llm_messages = ""
        if few_shot_example:
            llm_messages = "[INST]"

        for message in messages:
            if message.sender == "Human":
                llm_messages += str(message)
            elif message.sender == "AI":
                llm_messages += "[/INST] " + str(message)
                if not few_shot_example:
                    llm_messages += "</s>\n<s>[INST]"
        return llm_messages
