import logging
import time


class DisplayCallback:

    def debug(self, message: str):
        logging.debug(message)
