import os

from file_hadlers import read_json


class Configurator:
    def __init__(self, config_path):
        self.config_path = config_path

        self._is_exists_flag = False
        self.config = {}

        self._config_is_exists()
        self.read_config()

    def _config_is_exists(self):
        if os.path.exists(self.config_path):
            self._is_exists_flag = True
        else:
            self._is_exists_flag = False

    def read_config(self):
        if self._is_exists_flag:
            self.config = read_json(self.config_path)
            return self.config
        else:
            print('configuration file not found')

    def get_value(self, key):
        value = self.config.get(key, None)
        return value
