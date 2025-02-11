import threading
from time import sleep


class Controller:
    def __init__(self, client, server):
        self._client = client
        self._server = server

        # monitoring thread
        self.thread_1 = threading.Thread(target=self._start_read, args=(), daemon=True)
        self.thread_1.start()

        # server thread
        self.thread_2 = threading.Thread(target=self._start_listen, args=(), daemon=True)
        self.thread_2.start()

        # protection thread
        self.thread_3 = threading.Thread(target=self._start_protection, args=(), daemon=True)
        self.thread_3.start()

        # plc control counter thread
        self.thread_4 = threading.Thread(target=self._start_control_counter, args=(), daemon=True)
        self.thread_4.start()

    def _start_read(self):
        while True:
            self._client.read_data()
            # sleep(0.01)
            sleep(0.01)


    def _start_listen(self):
        while True:
            self._server.listen_port()
            sleep(0.000001)

    def _start_protection(self):
        while True:
            self._client.control_position_limits()
            sleep(0.000001)

    def _start_control_counter(self):
        while True:
            # self._client.update_time_delta()
            self._client.start_control_counter()
            sleep(1)
