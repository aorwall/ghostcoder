import time
from typing import List

from langchain.callbacks.base import BaseCallbackHandler
from langchain.prompts.base import StringPromptValue
from langchain.schema.language_model import BaseLanguageModel

from ghostcoder.schema import Message, Stats


class LLMWrapper:

    def __init__(self, llm: BaseLanguageModel):
        self.llm = llm

    def generate(self, sys_prompt: str, messages: List[Message], callback: BaseCallbackHandler = None) -> (str, Stats):
        starttime = time.time()

        prompt_value = "System: " + sys_prompt + "\n" + self.messages_to_prompt(messages)
        result = self.llm.generate_prompt([StringPromptValue(text=prompt_value)], callbacks=[callback])
        content = result.generations[0][0].text

        usage = Stats.from_dict(
            prompt=self.__class__.__name__,
            llm_output=result.llm_output,
            duration=time.time() - starttime)
        return content, usage

    def messages_to_prompt(self, messages: List[Message], few_shot_example: bool = False):
        llm_messages = ""
        for message in messages:
            llm_messages += "\n" + message.role + ": " + message.to_prompt()
        return llm_messages
