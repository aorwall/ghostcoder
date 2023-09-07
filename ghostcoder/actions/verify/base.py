import difflib
import logging
import re
from typing import List
from typing import Optional

from ghostcoder.actions.base import BaseAction
from ghostcoder.actions.write_code.prompt import get_implement_prompt, FEW_SHOT_PYTHON_1, ROLE_PROMPT
from ghostcoder.filerepository import FileRepository
from ghostcoder.llm.base import LLMWrapper
from ghostcoder.schema import Message, Stats
from ghostcoder.verify.verify_python_unittest import verify


class VerifyAction(BaseAction):

    def __init__(self,
                 llm: LLMWrapper,
                 role_prompt: Optional[str] = None,
                 sys_prompt_id: Optional[str] = None,
                 sys_prompt: Optional[str] = None,
                 repository: FileRepository = None,
                 auto_mode: bool = False,
                 few_shot_prompt: bool = False,
                 tries: int = 2):
        if not sys_prompt:
            sys_prompt = get_implement_prompt(sys_prompt_id)
        super().__init__(llm, sys_prompt)
        self.llm = llm
        self.repository = repository
        self.auto_mode = auto_mode
        self.tries = tries
        self.role_prompt = role_prompt
        self.few_shot_prompt = few_shot_prompt

    def execute(self, message: Message, message_history: List[Message] = []) -> List[Message]:
        logging.info("Execute the Write Code Action")

        failures = verify()
        if failures:
            # read code blocks
            code_blocks = []

        return self._execute(messages=[message], message_history=message_history, retry=0)

    def generate(self, messages: List[Message], history: List[Message] = []) -> (str, Stats):
        sys_prompt = ""
        if self.role_prompt:
            sys_prompt += self.role_prompt + "\n"
        else:
            sys_prompt += ROLE_PROMPT + "\n"

        sys_prompt += self.sys_prompt

        if self.few_shot_prompt:
            sys_prompt += "\n" + self.llm.messages_to_prompt(messages=FEW_SHOT_PYTHON_1, few_shot_example=True)
        return self.llm.generate(sys_prompt, history + messages)
