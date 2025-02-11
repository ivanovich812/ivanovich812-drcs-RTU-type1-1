import os
import json


class JsonHandler:
    def __init__(self, path, scope_path):

        self.path_monitor = path
        self.scope_path = scope_path

        self._check_directory(self.path_monitor)

    def _check_directory(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
            self.path_monitor = os.path.join(path, 'fc_axes_monitor.json')
        else:
            self.path_monitor = os.path.join(path, 'fc_axes_monitor.json')

    def write_json(self, data):
        with open(self.path_monitor, 'w') as plc_data_file:
            json.dump(data, plc_data_file, indent=4, sort_keys=False)

    @staticmethod
    def read_json(path):
        if os.path.exists(path):
            with open(path, 'r') as json_file:
                data = json.load(json_file)
                return data
        else:
            return None

    def add_to_json(self, key, value):
        if os.path.exists(self.scope_path):
            with open(self.scope_path, 'r+') as json_file:
                try:
                    data = json.load(json_file)
                    print('data:', data)
                    data[key] = value
                except json.decoder.JSONDecodeError:
                    data = None
                    print('oops')

            with open(self.scope_path, 'w+') as json_file:
                if data is not None:
                    json.dump(data, json_file, indent=4, sort_keys=False)
        else:
            print(f'error during json add operation [{self.scope_path}]')
