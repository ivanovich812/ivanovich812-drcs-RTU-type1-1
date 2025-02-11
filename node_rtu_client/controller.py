import sys
import threading
from time import sleep


class Controller:
    def __init__(self, client_a, client_b):
        self._client_a = client_a
        self._client_b = client_b

        # com a
        self.thread_a = threading.Thread(target=self._start_a, args=(), daemon=True)
        self.thread_a.start()

        # com b
        self.thread_b = threading.Thread(target=self._start_b, args=(), daemon=True)
        self.thread_b.start()


    def _start_a(self):
        while True:
            self._client_a.read_data()
            sleep(0.01)
            self._client_a.write_data()
            sleep(0.01)

    def _start_b(self):
        while True:
            self._client_b.read_data()
            sleep(0.01)
            self._client_b.write_data()
            sleep(0.01)





