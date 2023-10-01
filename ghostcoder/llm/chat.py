import time
from typing import List

from langchain.callbacks.base import BaseCallbackHandler
from langchain.chat_models.base import BaseChatModel
from langchain.schema import SystemMessage, AIMessage, HumanMessage

from ghostcoder.llm.base import LLMWrapper
from ghostcoder.schema import Message, Stats


class ChatLLMWrapper(LLMWrapper):

    def __init__(self, llm: BaseChatModel):
        super().__init__(llm)
        self.llm = llm

    def generate(self, sys_prompt: str, messages: List[Message], callback: BaseCallbackHandler = None) -> (str, Stats):
        starttime = time.time()
        llm_messages = [SystemMessage(content=sys_prompt)]

        for message in messages:
            if message.sender == "AI":
                llm_messages.append(AIMessage(content=message.to_prompt()))
            else:
                llm_messages.append(HumanMessage(content=message.to_prompt()))

        callbacks = [callback] if callback else []
        result = self.llm.generate([llm_messages], callbacks=callbacks)

        content = result.generations[0][0].text
        usage = Stats.from_dict(
            prompt=self.__class__.__name__,
            llm_output=result.llm_output,
            duration=time.time() - starttime)
        return content, usage
