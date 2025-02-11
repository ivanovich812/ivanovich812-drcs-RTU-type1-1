"""
Для добавления нового .json файла в опрос:
- добавить путь к файлу в словаре self.paths_dict с произвольным названием пути,
- для этого названия в словаре self.writable_variables добавить переменные разрешенные к записи из OPC UA сервера (writable variables)
- для передачи string просто выставить в клиенте opcua тип данных string и писать в json в "".
"""

from datetime import datetime
import time

from opcua import Server, ua
from json_handler import read_json, add_to_json


class OpcUaServer:
    def __init__(self):
        self.server = Server()
        self.server.set_security_policy([ua.SecurityPolicyType.NoSecurity])
        URL = 'opc.tcp://localhost:4840'
        self.paths_dict = {
            'fc_axes_monitor': "../DATA_SRV/AXES/fc_axes_monitor.json",
            'plc_io_monitor': "../DATA_SRV/PLC/plc_io_monitor.json",
            'plc_tasks': "../DATA_SRV/PLC/plc_tasks.json",
            'joint_points': "../DATA_SRV/DATA_POINTS/JOINT/joint_points.json",
            'rtc_control': "../DATA_SRV/RTC/rtc_control.json",

        }
        self.writable_variables = {
            'fc_axes_monitor': (
            ),
            'plc_io_monitor': (
                'in_cabinet_door_opened',
                'in_cabinet_overheat'
            ),
            'plc_tasks': (
                'out_gripper_1_1',
                'out_gripper_1_2',
                'out_ready',
                'out_gripper_2345',
                'out_enable_work'
            ),
            'joint_points': (
            ),
            'rtc_control': (
                "rtc_sub_work_widget_index",
                "rtc_joint_number"
            )

        }
        self.server.set_endpoint(URL)
        self.objects = self.server.get_objects_node()
        self.ns = self.server.register_namespace("rtu")
        self.opc_directories = dict()
        self.tags = dict()
        self.values = dict()
        self.old_values = dict()
        self.create_opc_directories()
        self.create_dict(self.tags, self.tags_sub_func)
        self.create_dict(self.old_values, self.old_values_sub_func)


    def create_dict(self, var_dict, sub_func):
        def fill_dict(data, path_name, temp_dict, opc_directory):
            for key, value in data.items():
                if isinstance(value, dict):
                    fill_dict(value, path_name, temp_dict, opc_directory)
                else:
                    sub_func(key, value, opc_directory, path_name, temp_dict)
                var_dict[path_name] = temp_dict

        for path_name, opc_directory in self.opc_directories.items():
            opc_directory = self.opc_directories[path_name]
            path = self.paths_dict[path_name]
            data = read_json(path)
            var_dict[path_name] = None
            temp_dict = {}
            fill_dict(data, path_name, temp_dict, opc_directory)

    def old_values_sub_func(self, key, value, opc_directory, path_name, temp_dict):
        temp_dict[key] = value

    def tags_sub_func(self, key, value, opc_directory, path_name, temp_dict):
        variable = key
        value = value
        tag = opc_directory.add_variable(self.ns, variable, value)

        if variable in self.writable_variables[path_name]:
            tag.set_writable()

        temp_dict[variable] = tag

    def values_sub_func(self, key, value, opc_directory, path_name, temp_dict):
        temp_dict[key] = value

    def create_opc_directories(self):
        for path_name in self.paths_dict:
            opc_directory = self.objects.add_object(self.ns, path_name)
            self.opc_directories[path_name] = opc_directory

    def read_write_tags(self):
        for path_name, values in self.values.items():
            for key, value in values.items():
                node = self.server.get_node(self.tags[path_name][key])
                client_value = node.get_value()

                if self.old_values[path_name][key] != client_value:
                    self.values[path_name][key] = client_value
                    add_to_json(self.paths_dict[path_name], key, client_value)
                    self.old_values[path_name][key] = self.values[path_name][key]
                else:
                    self.old_values[path_name][key] = self.values[path_name][key]
                    client_value = self.values[path_name][key]
                    if path_name == 'fc_axes_monitor':
                        dv = ua.DataValue(ua.Variant(self.values[path_name][key], ua.VariantType.Float))

                    else:
                        dv = ua.DataValue(ua.Variant(self.values[path_name][key]))
                    dv.SourceTimestamp = datetime.utcnow()
                    dv.ServerTimestamp = datetime.utcnow()
                    self.tags[path_name][key].set_value(dv)

    def run(self):
        self.server.start()
        self.server.set_server_name("RTU OPC UA Server")
        try:
            while True:
                self.create_dict(self.values, self.values_sub_func)
                self.read_write_tags()
                time.sleep(1)
        finally:
            self.server.stop()


if __name__ == "__main__":
    server = OpcUaServer('data/configopcua.ini')
    server.run()
