import json
import os


def _prepare_data(data, temp_data=None):
    if temp_data is None:
        tmp = {}
    else:
        tmp = temp_data

    for key, value in data.items():
        if isinstance(value, dict):
            _prepare_data(value, tmp)
        else:
            tmp[key] = value

    return tmp


# def read_json(filepath):
#     if os.path.exists(filepath):
#         with open(filepath, 'r') as file:
#             try:
#                 data = json.load(file)
#                 final_data = _prepare_data(data)
#                 return final_data
#             except json.decoder.JSONDecodeError:
#                 return {}

