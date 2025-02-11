import time
from datetime import datetime as dt, datetime
import struct
import serial
import minimalmodbus


class ClientRtu:
    def __init__(self, config, logger, model):
        self.config = config
        self.logger = logger
        self.model = model
        self._parity = {'N': serial.PARITY_NONE,
                        'E': serial.PARITY_EVEN,
                        'O': serial.PARITY_ODD}
        self._task_start_values = {
            '1': {
                'out_starting_type': 0,
                'out_motor_current_set_value': 0,
                'out_motor_speed_set_value': 0
                },
            '7': {
                'out_starting_type': 0,
                'out_motor_current_set_value': 0,
                'out_motor_speed_set_value': 0
                },
            '3': {
                'out_starting_type': 0,
                'out_motor_current_set_value': 0,
                'out_motor_speed_set_value': 0
            }
            }
        self._mappings = {}
        self._clients = {}
        self._connection_flags = {}
        self._make_connection_flags = {}
        self._error_counter= {}
        self._max_errors = 3
        self._define_slave_devices()
        self._define_nodes()
        self._make_connection()
        self._init_old_task_data()
        # self._create_sql_tables() # вообще не использовать!!!

    def _define_slave_devices(self):
        self._slave_devices = self.config.get_value('Server', 'slave address').split(',')

    def _define_nodes(self):
        for id in self._slave_devices:
            try:
                self._mappings[id] = self.config.get_value('_'.join([id, 'rtu_mapping']))
                self.logger.event('debug', f'ModbusRTU, slave address {id}: nodes defined successfully!')
            except Exception as e:
                self.logger.event('error', f'ModbusRTU, slave address {id}: error during nodes creation: {e}')
    def _make_connection(self):
        for id in self._slave_devices:
            try:
                client = minimalmodbus.Instrument(self.config.get_value('Server', 'port name'),
                                                       int(id),
                                                       debug=False)
                client.serial.baudrate = self.config.get_value('Server', 'baudrate')  # baudrate
                client.serial.bytesize = int(self.config.get_value('Server', 'bytesize'))
                client.serial.parity = self._parity.get(self.config.get_value('Server', 'parity'))
                client.serial.stopbits = int(self.config.get_value('Server', 'stopbits'))
                client.serial.timeout = float(self.config.get_value('Server', 'timeout'))  # seconds
                client.address = int(id)  # this is the slave address number
                client.mode = minimalmodbus.MODE_RTU  # rtu or ascii mode
                client.clear_buffers_before_each_transaction = True
                self.logger.event('debug', f"ModbusRTU, slave address {id}: Connection["
                                           f"{self.config.get_value('Server', 'port name')},"
                                           f"{client.address},"
                                           f"{client.serial.baudrate},"
                                           f"{client.serial.bytesize},"
                                           f"{client.serial.parity},"
                                           f"{client.serial.stopbits},"
                                           f"{client.serial.timeout}]  established!")
                self._connection_flags['_'.join([id, 'connection_flag'])] = 1
                self._make_connection_flags['_'.join([id, 'make_connection_flag'])] = 1
                self._clients[id]=client
                self._error_counter[id] = 0
            except Exception as e:
                self.logger.event('error', f'ModbusRTU, slave address {id}, make_connection: connection error: {e}')
                self._connection_flags['_'.join([id, 'connection_flag'])] = 0
                self._make_connection_flags['_'.join([id, 'make_connection_flag'])] = 0
            self.model.update_model(self._connection_flags)

    def _init_old_task_data(self):
        for id, mapping in self._mappings.items():
            if self._make_connection_flags['_'.join([id, 'make_connection_flag'])]:
                out1_signals = {}
                try:
                    out1_read_params = mapping['out1_parameters'].split(',')
                    out1_registers = self._read_registers(id, out1_read_params[0], out1_read_params[1],
                                                          out1_read_params[2])
                    out1_packed_string_var = struct.pack(out1_read_params[3], *tuple(out1_registers))
                    out1_unpacked_registers = struct.unpack(out1_read_params[4], out1_packed_string_var)
                    for name, raw_params in mapping.items():
                        params = raw_params.split(',')
                        if out1_unpacked_registers:
                            if name[:3] == 'out' and name != 'out1_parameters' and name != 'out2_parameters':
                                regs = out1_unpacked_registers[int(params[0])]
                                try:
                                    if name in self._task_start_values[id].keys():
                                        regs = 0
                                except:
                                    pass
                                out1_signals['_'.join([id, name])] = regs
                    self.model.update_task_model(out1_signals)
                    self._connection_flags['_'.join([id, 'connection_flag'])] = 1
                    self._make_connection_flags['_'.join([id, 'make_connection_flag'])] = 1
                except Exception as e:
                    self.logger.event('error', f"ModbusRTU, slave address {id}, init_old_task_data: {e}")
                    self._connection_flags['_'.join([id, 'connection_flag'])] = 0
                    self._make_connection_flags['_'.join([id, 'make_connection_flag'])] = 0
                self.model.update_model(self._connection_flags)

    def _read_registers(self, slave_address, registeraddress, number_of_registers, functioncode):
        id = slave_address
        registers = self._clients[id].read_registers(
            registeraddress = int(registeraddress, 16),
            number_of_registers = int(number_of_registers),
            functioncode = int(functioncode))
        return registers

    def read_data(self):
        for id, mapping in self._mappings.items():
            if self._make_connection_flags['_'.join([id, 'make_connection_flag'])]:
                in_signals = {}
                out1_signals = {}
                out2_signals = {}
                try:
                    # опрос 1301 - 130F
                    in_read_params = mapping['in_parameters'].split(',')
                    in_registers = self._read_registers(id, in_read_params[0], in_read_params[1], in_read_params[2])
                    in_packed_string_var = struct.pack(in_read_params[3], *tuple(in_registers))
                    in_unpacked_registers = struct.unpack(in_read_params[4], in_packed_string_var)
                    for name, raw_params in mapping.items():
                        params = raw_params.split(',')
                        if in_unpacked_registers:
                            if name[:2] == 'in'and name!='in_parameters':
                                in_signals['_'.join([id, name])] = in_unpacked_registers[int(params[0])]

                    # опрос 1000 - 100С
                    out1_read_params = mapping['out1_parameters'].split(',')
                    out1_registers = self._read_registers(id, out1_read_params[0], out1_read_params[1], out1_read_params[2])
                    out1_packed_string_var = struct.pack(out1_read_params[3], *tuple(out1_registers))
                    out1_unpacked_registers = struct.unpack(out1_read_params[4], out1_packed_string_var)
                    for name, raw_params in mapping.items():
                        params = raw_params.split(',')
                        if out1_unpacked_registers:
                            if name[:3] == 'out'and name!='out1_parameters' and name!='out2_parameters':
                                out1_signals['_'.join([id, name])] = out1_unpacked_registers[int(params[0])]

                    # опрос 1024
                    out2_read_params = mapping['out2_parameters'].split(',')
                    out2_registers = self._read_registers(id, out2_read_params[0], out2_read_params[1], out2_read_params[2])
                    out2_packed_string_var = struct.pack(out2_read_params[3], *tuple(out2_registers))
                    out2_unpacked_registers = struct.unpack(out2_read_params[4], out2_packed_string_var)
                    for name, raw_params in mapping.items():
                        params = raw_params.split(',')
                        if out2_unpacked_registers:
                            if name == 'out_shortcut_instruction_1':
                                out2_signals['_'.join([id, name])] = out2_unpacked_registers[int(params[0])]

                    signals =  {**in_signals, **out1_signals, **out2_signals}
                    self.model.update_model(signals)
                    if self._error_counter[id] == self._max_errors:
                        if self._connection_flags['_'.join([id, 'connection_flag'])] == 0:
                            self.logger.event('debug', f"ModbusRTU, slave address {id}: Connection is reestablished!")
                    count = self._error_counter[id] - 1
                    self._error_counter[id] = self._limit(0, self._max_errors, count)
                    self._connection_flags['_'.join([id, 'connection_flag'])] = 1
                except Exception as e:
                    count = self._error_counter[id] + 1
                    self._error_counter[id] = self._limit(0, self._max_errors, count)
                    if self._error_counter[id] == self._max_errors:
                        if self._connection_flags['_'.join([id, 'connection_flag'])] == 1:
                            self._connection_flags['_'.join([id, 'connection_flag'])] = 0
                            self.logger.event('error', f"ModbusRTU, slave address {id}: {e}")
                            signals = {}
                            for name, raw_params in mapping.items():
                                signals['_'.join([id, name])] = 0
                            self.model.update_model(signals)

                self.model.update_model(self._connection_flags)
            else:
                signals = {}
                for name, raw_params in mapping.items():
                    signals['_'.join([id, name])] = 0
                self.model.update_model(signals)

    def write_data(self):
        for id, mapping in self._mappings.items():
            if self._connection_flags['_'.join([id, 'connection_flag'])]:
                data = self.model.get_from_db()
                out1_signals = []
                out2_signals = []
                try:
                    # запись 1000 - 100С
                    out1_write_params = mapping['out1_parameters'].split(',')
                    for name, raw_params in mapping.items():
                        if name[:3] == 'out'and name!='out1_parameters' and name!='out2_parameters' and name!='out_shortcut_instruction_1':
                            params = raw_params.split(',')
                            out1_signals.append(data['_'.join([id, name])])

                    packed_string_var = struct.pack(out1_write_params[4], *tuple(out1_signals))
                    unpacked_var = struct.unpack(out1_write_params[3], packed_string_var)
                    unpacked_var = list(unpacked_var)

                    self._clients[id].write_registers(
                        registeraddress=int(out1_write_params[0], 16),
                        values=unpacked_var
                    )

                    # запись 1024
                    out2_write_params = mapping['out2_parameters'].split(',')
                    for name, raw_params in mapping.items():
                        if name=='out_shortcut_instruction_1':
                            params = raw_params.split(',')
                            out2_signals.append(data['_'.join([id, name])])

                    packed_string_var = struct.pack(out2_write_params[4], *tuple(out2_signals))
                    unpacked_var = struct.unpack(out2_write_params[3], packed_string_var)
                    unpacked_var = list(unpacked_var)

                    self._clients[id].write_registers(
                        registeraddress=int(out2_write_params[0], 16),
                        values=unpacked_var
                    )

                except Exception as e:
                    pass
                    # Контроль модбас соединения ведется по read функции. Пока счетчик не отработал сюда будут прилетать
                    # лишние ошибки записи, поэтому закомменчено.
                    # self.logger.event('error', f"ModbusRTU, slave address {id}: {e}")
                    # флаг включается не сразу а по счетчику в read функции, поэтому закомменчено.
                    # self._connection_flags['_'.join([id, 'connection_flag'])] = 0

    def _limit(self, min, max, value):
        if value < min:
            value = min
        elif value > max:
            value = max
        else: value = value
        return value

    # def _create_sql_tables(self):
    #     for id, mapping in self._mappings.items():
    #         for name, raw_params in mapping.items():
    #             params = raw_params.split(',')
    #             type = params[0]
    #             if type == 'bool':
    #                 value = False
    #                 self.model.update_model('_'.join([id, name]), value)
    #             elif type in ['H','h','L','l']:
    #                 value = 0
    #                 self.model.update_model('_'.join([id, name]), value)

