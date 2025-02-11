import json
import os

# TODO: DONE! add logger!!!


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


def delete_from_json(path, key):
    if _is_file_exists(path):
        data = read_json(path)
        result = data.pop(key, False)
        if not result:
            print(f'{key} not found in {path}')
        else:
            with open(path, 'w') as json_file:
                json.dump(data, json_file)
