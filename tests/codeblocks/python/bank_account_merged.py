import threading

class BankAccount:
    def __init__(self):
        self._balance = 0
        self._lock = threading.Lock()
        self._is_open = False
