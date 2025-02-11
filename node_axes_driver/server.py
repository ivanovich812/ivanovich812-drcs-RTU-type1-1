import socket
from datetime import datetime as dt


class Server:

    def __init__(self, client, logger):
        self._client = client
        self._logger = logger

        self._sock = socket.socket()
        try:
            self._sock.bind(('', 9090))
        except OSError as e:
            self._logger.event('error', f'FCMonitor: Server error: {e}.')

    def listen_port(self):
        print('Listening to port...')
        self._sock.listen(1)
        conn, address = self._sock.accept()
        data = conn.recv(200)
        if data:
            self._logger.event('debug', f'{data}')
            decoded_data = data.decode()
            print('decoded_data: ', decoded_data)
            if 'all' not in decoded_data:
                if 'define_axis' in decoded_data:
                    self._client.calculate_axes_command(decoded_data)
                else:
                    self._client.send_single_command(decoded_data)
            else:
                self._client.check_command_for_all(decoded_data)
