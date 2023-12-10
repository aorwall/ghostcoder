import logging
import time
from typing import List

from ghostcoder.schema import Item


class DisplayCallback:

    def on_new_item(self, item: Item):
        pass

    def on_new_items(self, items: List[Item]):
        for item in items:
            self.on_new_item(item)

    def debug(self, message: str):
        logging.debug(message)
