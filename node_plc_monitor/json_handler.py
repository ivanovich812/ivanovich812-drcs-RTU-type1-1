# Протестить без этого класса и удалить файл!

# import json
# import os
#
#
# class JsonHandler:
#     def __init__(self, path):
#
#         self.path_monitor = path
#         self.path_task = path
#
#         self._check_directory(self.path_monitor)
#
#     def _check_directory(self, path):
#         if not os.path.exists(path):
#             os.makedirs(path)
#             self.path_monitor = os.path.join(path, 'plc_io_monitor.json')
#             self.path_task = os.path.join(path, 'plc_tasks.json')
#         else:
#             self.path_monitor = os.path.join(path, 'plc_io_monitor.json')
#             self.path_task = os.path.join(path, 'plc_tasks.json')
#
#     def write_json(self, data):
#         with open(self.path_monitor, 'w') as plc_data_file:
#             json.dump(data, plc_data_file, indent=4, sort_keys=False)
#
#     def read_json(self):
#         with open(self.path_task, 'r') as plc_task_file:
#             try:
#                 data = json.load(plc_task_file)
#                 return data
#             except json.decoder.JSONDecodeError:
#                 return None
