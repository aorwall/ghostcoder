import sys

from ghostcoder.ipython_callback import DisplayCallback
from ghostcoder.schema import Message


class SysoutCallback(DisplayCallback):

    def __init__(self, display_id: str = None):
        self.display_id = display_id
        self.text = ""

    def ai_stream(self, token: str):
        if not self.text:

            print("AI:")
        self.text += token
        sys.stdout.write(token)
        sys.stdout.flush()

    def display_message(self, message: Message):
        if self.text:
            self.text = ""
        else:
            print(message.to_prompt())
