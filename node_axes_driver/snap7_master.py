import math as m
import numpy as np
import json
from kinematics import solve_direct_problem, inverse_kinematic
import snap7


def _get_indexes(params):
    params = str(params)
    data = params.split('.')
    db_number = int(data[0])
    start = int(data[1])
    size = int(data[2])
    return db_number, start, size


def _update_coordinates(matrix, params):
    raw_matrix = matrix.copy()
    axis = params[0]
    direction = float(params[1])
    frame = params[3]
    trans_matrix = None
    new_homo_matrix = None
    if axis == 'X':
        trans_matrix = np.array([[1, 0, 0, direction], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]).reshape(4, 4)

    elif axis == 'Y':
        trans_matrix = np.array([[1, 0, 0, 0], [0, 1, 0, direction], [0, 0, 1, 0], [0, 0, 0, 1]]).reshape(4, 4)

    elif axis == 'Z':
        trans_matrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, direction], [0, 0, 0, 1]]).reshape(4, 4)

    if frame == 'BASE':
        new_homo_matrix = trans_matrix @ raw_matrix
    elif frame == 'TOOL':
        new_homo_matrix = raw_matrix @ trans_matrix
    return new_homo_matrix


def _update_orientation(matrix, params):
    raw_matrix = matrix.copy()
    axis = params[0]
    rotation = float(params[1])
    frame = params[3]
    trans_matrix = None
    new_homo_matrix = None

    if axis == 'X':
        trans_matrix = np.array([[1, 0, 0, 0],
                                 [0, m.cos(m.radians(rotation)), -m.sin(m.radians(rotation)), 0],
                                 [0, m.sin(m.radians(rotation)), m.cos(m.radians(rotation)), 0],
                                 [0, 0, 0, 1]]).reshape(4, 4)

    elif axis == 'Y':
        trans_matrix = np.array([[m.cos(m.radians(rotation)), 0, m.sin(m.radians(rotation)), 0],
                                 [0, 1, 0, 0],
                                 [-m.sin(m.radians(rotation)), 0, m.cos(m.radians(rotation)), 0],
                                 [0, 0, 0, 1]]).reshape(4, 4)

    elif axis == 'Z':
        trans_matrix = np.array([[m.cos(m.radians(rotation)), -m.sin(m.radians(rotation)), 0, 0],
                                 [m.sin(m.radians(rotation)), m.cos(m.radians(rotation)), 0, 0],
                                 [0, 0, 1, 0],
                                 [0, 0, 0, 1]]).reshape(4, 4)

    if frame == 'BASE':
        transformed_rotation = trans_matrix[0:3, 0:3] @ raw_matrix[0:3, 0:3]
        zeros = np.zeros(shape=(1, 3))
        pos = raw_matrix[0:4, 3:4]
        new_homo_matrix = np.column_stack((np.vstack((transformed_rotation, zeros)), pos))
    elif frame == 'TOOL':
        new_homo_matrix = raw_matrix @ trans_matrix
    return new_homo_matrix


def _calculate_speed(target_position, current_position, time):
    # calculate speed. Position data in FC units (not angles!)
    delta_position = []
    speed = []
    for t_pos, c_pos in zip(target_position, current_position):
        delta = t_pos - c_pos # gefran
        # delta = abs(t_pos - c_pos) / 100.0 #sew eurodrive
        delta_position.append(delta)

    for pos in delta_position:
        try:
            # v = int(round((abs(pos/65536) / time) * 60.0, 2)) # gefran
            v = int(round((abs(pos / 4096) / time) * 60.0, 2))  # sew moviedrive (об/мин)
            # v = int(round((pos / time) * 60.0, 2)) # sew eurodrive
            if v > 3200: # ограничение в ПЧ
                v = 3200
            if v > 1:
                speed.append(v)
            else:
                speed.append(1)
        except ZeroDivisionError:
            speed.append(0)
    return speed



def _calculate_time(start_matrix, end_matrix, speed):
    x_1 = start_matrix[0][3]
    y_1 = start_matrix[1][3]
    z_1 = start_matrix[2][3]
    x_2 = end_matrix[0][3]
    y_2 = end_matrix[1][3]
    z_2 = end_matrix[2][3]

    s = m.sqrt((x_2 - x_1) ** 2 + (y_2 - y_1) ** 2 + (z_2 - z_1) ** 2)
    try:
        t = s / speed
    except ZeroDivisionError:
        t = 0

    return t


def _calculate_acceleration(speed, time):
    acc = []
    for value in speed:
        try:
            # a = (value / time) * 10
            # a = (value/60) / time # об/сек2
            a = 50 * 1000 / ((value / 60) / time)  # сек (как в документации ПЧ)

            if a > 100000: # мин ускорение 20000мсек(время выхода на макс скорость) ограничение в ПЧ
                a = 100000
            if a < 10: # макс ускорение 10мсек ограничение в ПЧ
                a = 10

        except ZeroDivisionError:
            a = 0
        # acc.append(int(a * 5))
        acc.append(int(a / 5)) # for in sec
    return acc


class Client:
    MANUAL_LINEAR_SPEED_MAX = 100  # maximum speed in manual linear mode [mm/s]

    def __init__(self, config, logger, data_model, protocol_path, json_handler):

        self._config = config
        self.logger = logger
        self._data_model = data_model
        self._protocol_path = protocol_path
        self._json_handler = json_handler

        self._thread_1_client = None # для чтения
        self._thread_2_client = None # для записи
        self._thread_4_client = None # для таймера PLC connection

        self._control_counter = 0 # Счетчик (запись от ЧМИ)
        self._time_delta = 1  # Временной промежуток проверки счетчика (plc data type: Time, sec)

        self._nodes = None
        self._speed_data = None
        self._protocol = None
        self._slaves = None
        self._unreachable_slaves = []
        self._temp_homogenous_matrix = None
        self._limit_flag = False
        self._jog_speed_value = 0

        self._cmd_dict = {'go_to': self._prepare_go_to_command,
                          'linear_jog': self._linear_jog,
                          'reorient_jog': self._reorient_jog}
        self._robot_parameters = {}
        self._position_limits = []

        self._read_robot_parameters()
        self._define_position_limits()
        self._define_nodes()
        self._define_speed_data()
        self._define_protocol()
        self._make_thread_1_connection()
        self._make_thread_2_connection()
        self._make_thread_4_connection()
        # self.calibration_by_last_db_data()
        # self._execute_init_cmd()


    def start_control_counter(self):
        if self.connection_flag_4:
            self._control_counter += 1
            plc = self._thread_4_client
            plc.db_write(5, 0, self._control_counter.to_bytes(1, byteorder="big", signed=True))

            if self._control_counter > 100:
                self._control_counter = 0

    def update_time_delta(self):
        if self.connection_flag_4:
            plc = self._thread_4_client
            # ???? как записывать в plc-тип данных TIME ???? предложить Степанову писать byte и конвертировать уже в ПЛК
            plc.db_write(5, 2, self._time_delta.to_bytes(1, byteorder="big", signed=True))

    def _execute_init_cmd(self):
        self.check_command_for_all('all:init')

    def calibration_by_last_db_data(self): # пытался сделать калибровку последними значениями из базы данных
        current_raw_position = self._data_model.read_raw_position()
        print(current_raw_position)
        cmd_pack = {
         "CW_0000000_1": [7, 0, 1, 0, [0, 0, 0, 0, 0, 0]],
         "raw_position": [7, 8, 4, 1, current_raw_position],
         "CW_1000001": [7, 0, 1, 0, [65, 65, 65, 65, 65, 65]],
         "CW_0000000_2": [7, 0, 1, 0, [0, 0, 0, 0, 0, 0]]
        }
        self._send_simple_command_for_all(cmd_pack)

    def _read_robot_parameters(self):
        self._robot_parameters = self._data_model.get_robot_parameters()

    def _define_position_limits(self):
        self._position_limits = list(self._robot_parameters.get('axes_limits').values())

    def _define_nodes(self):
        self._nodes = self._config.get_value('Registers')
        self._data_model.add_parameters(self._nodes.keys())

    def _define_speed_data(self):
        self._speed_data = self._config.get_value('Axes_max_speed')

    def _define_protocol(self):
        self._protocol = self._json_handler.read_json(self._protocol_path)

    def _make_thread_1_connection(self):
        try:
            self._thread_1_client = snap7.client.Client()
            self._thread_1_client.connect(self._config.get_value('Server', 'ip_address'),
                             int(self._config.get_value('Server', 'rack')),
                             int(self._config.get_value('Server', 'slot')))

            self.logger.event('debug', 'PLC-axes-driver-thread_1-client: Connection established!')
            self.connection_flag = True
        except Exception as e:
            self.logger.event('error', f'PLC-axes-driver-thread_1-client: connection error: {e}')
            self.connection_flag = False

    def _make_thread_2_connection(self):
        try:
            self._thread_2_client = snap7.client.Client()
            self._thread_2_client.connect(self._config.get_value('Server', 'ip_address'),
                             int(self._config.get_value('Server', 'rack')),
                             int(self._config.get_value('Server', 'slot')))

            self.logger.event('debug', 'PLC-axes-driver-thread_2-client: Connection established!')
            self.connection_flag = True
        except Exception as e:
            self.logger.event('error', f'PLC-axes-driver-thread_2-client: connection error: {e}')
            self.connection_flag = False

    def _make_thread_4_connection(self):
        try:
            self._thread_4_client = snap7.client.Client()
            self._thread_4_client.connect(self._config.get_value('Server', 'ip_address'),
                             int(self._config.get_value('Server', 'rack')),
                             int(self._config.get_value('Server', 'slot')))

            self.logger.event('debug', 'PLC-axes-driver-thread_4-client: Connection established!')
            self.connection_flag_4 = True
        except Exception as e:
            self.logger.event('error', f'PLC-axes-driver-thread_4-client: connection error: {e}')
            self.connection_flag_4 = False

    def _read_device(self):
        # print('_read_device!!!')
        plc = self._thread_1_client
        for parameter, register in self._nodes.items():
            register = json.loads(register)
            # print('register: ', register)
            for i, reg in enumerate(register):
                # print('i: ', i)
                # print('reg: ', reg)
                db_number, start, size = _get_indexes(reg)
                # print('db_number, start, size: ', db_number, start, size)
                try:
                    data = plc.db_read(db_number, start, size)
                    value = int.from_bytes(data[0:size], 'big', signed=True)
                    self._data_model.update_model(f'{parameter}',  # main_key
                                                  'axis_' + str(i + 1) + f'_{parameter}',  # sub-key
                                                  value)  # value
                except Exception as e:
                    self.logger.event('error', f"PLC-axes-driver-client: '{parameter}' could not read from server [{e}]")
                    # self.connection_flag = False
                    return None

    def _read_data(self):
        # print('self.connection_flag: ', self.connection_flag)
        if self.connection_flag:
            self._read_device()

    def read_data(self):
        self._read_data()

    def control_position_limits(self):
        pass

    def send_single_command(self, cmd):
        print('cmd: ', cmd)
        cmd_params = cmd.split(':')
        print('cmd_params: ', cmd_params)

        try:
            plc = self._thread_2_client
            i = int(cmd_params[0]) - 1
            print('i: ', i)
            print('plc: ', plc)
            cmd_pack = self._protocol[cmd_params[1]]
            print('cmd_pack: ', cmd_pack)
            for parameter, value in cmd_pack.items():
                print('parameter: ', parameter)
                if parameter == 'speed_setpoint':
                    self._jog_speed_value = abs(int(int(self._speed_data[cmd_params[0]]) * (int(cmd_params[2]) / 100)))
                    value[4][i] = self._jog_speed_value
                    plc.db_write(value[0], value[1] + value[2]*i, value[4][i].to_bytes(value[2], byteorder="big", signed=value[3]))
                    value[4][i] = 0
                elif parameter == "position_setpoint":
                    speed = int(cmd_params[2])
                    direction = int(speed/abs(speed))
                    plc.db_write(value[0], value[1] + value[2]*i, (direction * value[4][i]).to_bytes(value[2], byteorder="big", signed=value[3]))
                else:
                    plc.db_write(value[0], value[1] + value[2]*i, value[4][i].to_bytes(value[2], byteorder="big", signed=value[3]))
        except Exception as e:
            self.logger.event('error', f'{e}')

    def calculate_axes_command(self, cmd):
        print('Calculate axes command!============================')
        print('cmd: ', cmd)
        cmd_params = cmd.split(':')
        print('cmd_params: ', cmd_params)

        i = int(cmd_params[0]) - 1
        print('i: ', i)
        angle = float(cmd_params[2])
        print('angle: ', angle)
        n = list(self._robot_parameters['n'].values())
        print('n[i]: ', n[i])
        position = int((4096 / 360) * angle * n[i])
        print('position: ', position)

        try:
            plc = self._thread_2_client

            sw = 0
            plc.db_write(7, (0 + i*1), sw.to_bytes(1, byteorder="big", signed=False))

            plc.db_write(7, (8 + i*4), position.to_bytes(4, byteorder="big", signed=True))

            sw = 65
            plc.db_write(7, (0 + i*1), sw.to_bytes(1, byteorder="big", signed=False))

            sw = 0
            plc.db_write(7, (0 + i*1), sw.to_bytes(1, byteorder="big", signed=False))

        except Exception as e:
            self.logger.event('error', f'{e}')

    def check_command_for_all(self, cmd):
        cmd_params = cmd.split(':')
        print('cmd_params: ', cmd_params)
        cmd_pack = self._protocol.get(cmd_params[1], None)
        print('cmd_pack: ', cmd_pack)
        # case of simple command, for example 'all:stop'
        if len(cmd_params) == 2 and cmd_pack is not None:
            self._send_simple_command_for_all(cmd_pack)
        # case of not simple command, for example 'all:go_to:[values]'
        elif len(cmd_params) >= 3 and cmd_pack is not None:
            method = self._cmd_dict.get(cmd_params[1], None)
            if method is not None:
                method(cmd_pack, cmd_params[2:])
            else:
                print(f'wrong command: {cmd}')
        else:
            print(f'wrong command: {cmd}')

    def _send_simple_command_for_all(self, cmd_pack):
        print("def: _send_simple_command_for_all", cmd_pack)
        device = self._thread_2_client
        for key, value in cmd_pack.items():
            byte_array = bytearray([])
            for val in value[4]:
                byte_array.extend(val.to_bytes(value[2], byteorder="big", signed=value[3]))
            device.db_write(value[0], value[1], byte_array)

    def _where_are_you(self): # function for reading by bytearray (tested!)
        # read current position of all axes (in FC units, not angles)
        positions = []
        cmd = self._protocol['where_are_you']['current_position']
        plc = self._thread_2_client
        data = plc.db_read(cmd[0], cmd[1], 6 * cmd[2])
        for i in range(cmd[1], (cmd[2] * 6), cmd[2]):
            positions.append(int.from_bytes(data[i:(i + cmd[2])], 'big', signed=True))
        return positions

    def _angles_to_fc_units(self, position_data):
        # calculate positions in FC units from positions in angles
        in_fc_units = []
        n = self._robot_parameters['n'].values()
        for angle, n_coefficient in zip(position_data, n):
            value = (4096/360) * angle * n_coefficient
            in_fc_units.append(int(round(value, 2)))  # old round parameter = 0
        return in_fc_units

    def _fc_position_to_angles(self, position_data):
        angles = []
        n = self._robot_parameters['n'].values()
        for fc_pos, n_coefficient in zip(position_data, n):
            angles.append(fc_pos * (360 / 4096) / n_coefficient)
        return angles

    def _prepare_go_to_command(self, cmd_pack, data):
        print('_prepare_go_to_command =============================')
        print('cmd_pack: ', cmd_pack)
        print('data: ', data)
        if not self._unreachable_slaves:
            angles_target_position = list(map(float, data[0].strip('[]').split(',')))
            print('angles_target_position: ', angles_target_position)
            fc_units_target_position = self._angles_to_fc_units(angles_target_position)
            print('fc_units_target_position: ', fc_units_target_position)
            fc_units_current_position = self._where_are_you()
            print('fc_units_current_position: ', fc_units_current_position)
            time = int(data[1])  # it is speed percent value 1% = 1 sec
            print('time: ', time)
            speed = _calculate_speed(fc_units_target_position, fc_units_current_position, time)
            print('speed: ', speed)
            acceleration = _calculate_acceleration(speed, time)
            print('acceleration: ', acceleration)
            deceleration = _calculate_acceleration(speed, time)
            print('deceleration: ', deceleration)
            self.logger.event(
                'info',
                f'fc_units_current_position={fc_units_current_position} , '
                f'fc_units_target_position={fc_units_target_position}, speed={speed}, acceleration={acceleration}, time={time}')
            msg = {'position_setpoint': fc_units_target_position,
                   'speed': speed,
                   'acceleration': acceleration,
                   'deceleration': deceleration
                   }
            self._send_go_to_command(cmd_pack, msg)
        else:
            print(self._unreachable_slaves, 'offline!')

    def _send_go_to_command(self, cmd_pack, msg):
        print('def _send_go_to_command: =======================================')
        print('cmd_pack: ', cmd_pack)
        print('msg: ', msg)
        plc = self._thread_2_client
        for key, value in msg.items():
            cmd_data = cmd_pack[key]
            print('cmd_data: ', cmd_data)
            byte_array = bytearray([])
            for val in value:
                byte_array.extend(val.to_bytes(cmd_data[2], byteorder="big", signed=cmd_data[3]))
            plc.db_write(cmd_data[0], cmd_data[1], byte_array)

    def _linear_jog(self, cmd_pack, params):
        print('DEF_LINEAR_JOG: =======================================')
        print('cmd_pack: ', cmd_pack)
        print('params: ', params)
        inverse_solution = None
        current_position = self._where_are_you()  # in FC units
        print('current_position: ', current_position)
        angles = self._fc_position_to_angles(current_position)
        dh = self._robot_parameters.get('dh', None)
        tool_frame_offset = self._robot_parameters.get('TOOL', None)
        homogeneous_matrix = solve_direct_problem(angles, dh, tool_frame_offset)
        print('homogeneous_matrix: ', homogeneous_matrix)
        if homogeneous_matrix is not None:
            updated_homogeneous_matrix = _update_coordinates(homogeneous_matrix, params)
            # inverse solution in angles (not FC units!) need to convert in FC units
            if angles[4] > 0:
                inverse_solution = inverse_kinematic.InverseKinematic(updated_homogeneous_matrix, dh,
                                                                      tool_frame_offset).inverse_solution()[
                    '1']  # solution 1 of inverse kinematic problem for joint 5 > 0
            if angles[4] < 0:
                inverse_solution = inverse_kinematic.InverseKinematic(updated_homogeneous_matrix, dh,
                                                                      tool_frame_offset).inverse_solution()[
                    '5']  # solution 5 of inverse kinematic problem for joint 5 < 0
            if abs(angles[4] - angles[3]) != 0:
                inverse_solution_in_fc = self._angles_to_fc_units(inverse_solution)  # converting in FC units
                linear_speed = self.MANUAL_LINEAR_SPEED_MAX * int(params[2]) / 100
                # linear_speed = self.MANUAL_LINEAR_SPEED_MAX * int(params[2])
                time = _calculate_time(homogeneous_matrix, updated_homogeneous_matrix, linear_speed) #sec

                print('inverse_solution_in_fc: ', inverse_solution_in_fc)
                print('current_position______: ', current_position)

                speed = _calculate_speed(inverse_solution_in_fc, current_position, time) # об/мин
                print('speed: ', speed)
                print('time: ', time)
                acceleration = _calculate_acceleration(speed, time) # об/сек2
                print('acceleration: ', acceleration)
                deceleration = _calculate_acceleration(speed, time)
                print('deceleration: ', deceleration)

                msg = {'position_setpoint': inverse_solution_in_fc,
                       'speed': speed,
                       'acceleration': acceleration,
                       'deceleration': deceleration
                       }
                print('msg: ', msg)

                self._send_go_to_command(cmd_pack, msg)

    def _reorient_jog(self, cmd_pack, params):
        inverse_solution = None
        current_position = self._where_are_you()  # in FC units
        angles = self._fc_position_to_angles(current_position)
        dh = self._robot_parameters.get('dh', None)
        tool_frame_offset = self._robot_parameters.get('TOOL', None)
        homogeneous_matrix = solve_direct_problem(angles, dh, tool_frame_offset)
        if homogeneous_matrix is not None:
            updated_homogeneous_matrix = _update_orientation(homogeneous_matrix, params)
            # inverse solution in angles (not FC units!) need to convert in FC units
            if angles[4] > 0:
                inverse_solution = \
                    inverse_kinematic.InverseKinematic(updated_homogeneous_matrix, dh,
                                                       tool_frame_offset).inverse_solution()[
                        '1']  # solution 1 of inverse kinematic problem for joint 5 > 0
            if angles[4] < 0:
                inverse_solution = \
                    inverse_kinematic.InverseKinematic(updated_homogeneous_matrix, dh,
                                                       tool_frame_offset).inverse_solution()[
                        '5']  # solution 5 of inverse kinematic problem for joint 5 < 0
            if abs(angles[4] - angles[3]) != 0:
                inverse_solution_in_fc = self._angles_to_fc_units(inverse_solution)  # converting in FC units
                speed = self.MANUAL_LINEAR_SPEED_MAX * int(params[2]) / 100
                time = (abs(float(params[1])) / speed) if speed else 0
                speed = _calculate_speed(inverse_solution_in_fc, current_position, time)
                acceleration = _calculate_acceleration(speed, time)
                deceleration = _calculate_acceleration(speed, time)
                msg = {'position_setpoint': inverse_solution_in_fc,
                       'speed': speed,
                       'acceleration': acceleration,
                       'deceleration': deceleration
                       }

                self._send_go_to_command(cmd_pack, msg)
