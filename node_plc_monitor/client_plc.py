import struct

import snap7
import time
from datetime import datetime as dt, datetime


class ClientPlc:
    # TODO: cyclic connection need w/o 100500 error messages in log
    def __init__(self, config, logger, model):
        self.config = config
        self.logger = logger
        self.model = model
        self.mapping = None
        self.plc = None
        self.connection_flag = False
        self._reading_error = False
        self._types = {'bool': self._read_bool_data,
                       'int': self._read_int_data}

        self._define_nodes()
        self._make_connection()
        # self._create_sql_tables()

    def _define_nodes(self):
        try:
            self.mapping = self.config.get_value('plc_mapping')
            self.logger.event('debug', f'PLC: nodes defined successfully!')
        except Exception as e:
            self.logger.event('error', f'PLC: error during nodes creation: {e}')

    def _make_connection(self):
        try:
            self.plc = snap7.client.Client()
            self.plc.connect(self.config.get_value('Server', 'ip_address'),
                             int(self.config.get_value('Server', 'rack')),
                             int(self.config.get_value('Server', 'slot')))

            self.logger.event('debug', 'PLC: Connection established!')
            self.connection_flag = True
        except Exception as e:
            self.logger.event('error', f'PLC: connection error: {e}')
            self.connection_flag = False

    def _read_int_data(self, db_number, start_byte, size, node=None):
        try:
            var = self.plc.db_read(db_number, start_byte, size)
            value = int.from_bytes(var[0:size], 'big')
            return var, value
        except Exception as e:
            self.logger.event('error', f"PLC: '{node}' could not read from server [{e}]")
            self.connection_flag = False
            return None

    def _read_bool_data(self, db_number, start_byte, bit_number):
        try:
            _bytes = self.plc.db_read(db_number, start_byte, 1)
            value = snap7.util.get_bool(_bytes, 0, bit_number)
            return _bytes, value
        except Exception as e:
            self.logger.event('error', f"PLC: could not read from server [{e}]")
            self.connection_flag = False
            return None

    def read_data(self):
        if self.connection_flag:
            in_out_signals = {}
            raw_signals = {}
            # ai_signals = {}
            try:
                in_out_read_params = self.mapping['in_parameters'].split(',')
                _in_out_bytes = self.plc.db_read(db_number=int(in_out_read_params[0]), start=int(in_out_read_params[1]), size=int(in_out_read_params[2]))
                for name, raw_params in self.mapping.items():
                    params = raw_params.split(',')
                    if name!='in_parameters':
                        if name[:2] == 'in' or name[:3] == 'out':
                            value = snap7.util.get_bool(_in_out_bytes, byte_index=int(params[2]), bool_index=int(params[3]))
                            in_out_signals[name]=value

                raw_read_params = self.mapping['raw_parameters'].split(',')
                _raw_bytes = self.plc.db_read(db_number=int(raw_read_params[0]), start=int(raw_read_params[1]), size=int(raw_read_params[2]))
                unpacked_raw_reg = struct.unpack(">LLLL LLLL", _raw_bytes)
                for name, raw_params in (self.mapping.items()):
                    params = raw_params.split(',')
                    if name!='raw_parameters':
                        if name[:3] == 'raw':
                            raw_signals[name] = unpacked_raw_reg[int(params[0])]

                # ai_read_params = self.mapping['ai_parameters'].split(',')
                # _ai_bytes = self.plc.db_read(db_number=int(ai_read_params[0]), start=int(ai_read_params[1]), size=int(ai_read_params[2]))
                # unpacked_ai_reg = struct.unpack("HHHH HHHH", _ai_bytes)
                # for name, ai_params in (self.mapping.items()):
                #     params = ai_params.split(',')
                #     if name!='ai_parameters':
                #         if name[:2] == 'ai':
                #             ai_signals[name] = unpacked_ai_reg[int(params[0])]

                # signals = {**in_out_signals, **raw_signals, **ai_signals}
                signals = {**in_out_signals, **raw_signals}
                self.model.update_model_2(signals)

            except Exception as e:
                self.logger.event('error', f"PLC: {e}")
                self.connection_flag = False

    def write_data(self):
        if self.connection_flag:
            data = self.model.get_from_db()
            for tag, value in data.items():
                try:
                    params = self.mapping.get(tag, None).split(',')
                    _type = params[0]
                    if _type == 'bool':
                        if self.connection_flag:
                            _bytes, _value = self._read_bool_data(int(params[1]), int(params[2]), int(params[3]))
                            snap7.util.set_bool(_bytes, 0, int(params[3]), value)
                            self.plc.db_write(int(params[1]), int(params[2]), _bytes)
                        else:
                            self.logger.event('error', 'PLC: could not send data to server')
                except Exception as e:
                    self.logger.event('error', f'PLC: {tag}: {e}')
        t2 = datetime.now()

    def _create_sql_tables(self):# Использовать для создания таблиц plc_monitor когда нет соединения с ПЛК (расскомментить в init)
        for name, raw_params in self.mapping.items():
            params = raw_params.split(',')
            type = params[0]
            if type == 'bool':
                value = False
                self.model.update_model(name, value)
            elif type == 'int':
                value = 0
                self.model.update_model(name, value)

