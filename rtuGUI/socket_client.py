import socket


class SocketClient:
    def __init__(self, config):
        self._config = config

        self._ip = None
        self._port = None
        self._socket = None
        self._is_connected = False

        self._configure_connection()

    def _configure_connection(self):
        self._ip = self._config.get_value('driver_server_ip')
        self._port = self._config.get_value('driver_server_port')

    def send_data(self, data: str):
        print('send_data: ', data)
        try:
            self._socket = socket.socket()
            self._socket.settimeout(0.001)
            self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self._socket.connect((self._ip, self._port))
            self._socket.send(data.encode())
            self._socket.close()
        except Exception as e:
            pass
