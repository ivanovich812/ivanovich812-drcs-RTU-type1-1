import configparser
import os


class Configurator:
    def __init__(self, filepath, logger):
        self.filepath = filepath
        self.logger = logger

        self.file_exists = False
        self.configuration = {}

        self._check_config_file()
        self._create_config()

    def _check_config_file(self):
        self.file_exists = os.path.exists(self.filepath)

    def _create_config(self):
        config = configparser.ConfigParser()
        if self.file_exists:
            config.read(self.filepath)
            tmp = {section: {option: config.get(section, option).strip("'") for option in config.options(section)}
                   for section in config.sections()}
            self.configuration = tmp
            self.logger.event('debug', 'ModbusRTU: Configuration created')
        else:
            self.logger.event('error', f"ModbusRTU: Configuration file [{self.filepath}] doesn't exists")

    def get_value(self, section=None, option=None):
        try:
            parameter = self.configuration[section][option]
            return parameter
        except KeyError:
            parameter = self.configuration[section]
            return parameter
        except Exception as e:
            self.logger.event(f'PLC: get setting {section}, {option} error {e}')
            return None
