import json
import os

def _is_file_exists(path):
    return os.path.exists(path)

def read_json(path):
    if _is_file_exists(path):
        with open(path) as json_file:
            try:
                data = json.load(json_file)
                return data
            except json.decoder.JSONDecodeError:
                return None
    else:
        print(f'json {path} not found')

def add_to_json(path, key, value):
    if _is_file_exists(path):
        data = read_json(path)
        data[key] = value
        with open(path, 'w') as json_file:
            json.dump(data, json_file, indent=4, sort_keys=False)
    else:
        print(f'error during json add operation [{path}]')


