"""
Запись в текстовый файл параметров оси rtu (с форматированием строки в нужный формат).
"""
import math
import sys
from logger import Logger
sys.path.append('../')
from SQL.sql_client import SQLClient
# from Axe_1 import convert_angle_resolver_motor, convert_angle_resolver
import snap7



def record_values(self):
    logger = Logger()
    sql_client = SQLClient(logger, name='axes_calculating')
    data_plc = sql_client.read_plc_io_monitor()
    axes_data = sql_client.read_fc_axes_monitor()

    plc = snap7.client.Client()
    plc.connect('192.168.100.101', 0, 2)
    positions = []
    cmd = [2, 0, 4]
    data = plc.db_read(cmd[0], cmd[1], 6 * cmd[2])
    for i in range(cmd[1], (cmd[2] * 6), cmd[2]):
        positions.append(int.from_bytes(data[i:(i + cmd[2])], 'big', signed=True))
    print(positions)

    raw_position_4_ext = data_plc["raw_position_4_ext"]
    axis_4_raw_position_resolver_motor = positions[3]
    axis_4_actual_position = axes_data["actual_position"]["axis_4_actual_position"]

    # '%-*s' - выравнивание по левому краю, '%*s' - по правому.
    rec = ('%-*s' % (20, str(axis_4_actual_position))) \
          + '  |  ' + ('%-*s' % (6, str(raw_position_4_ext))) \
          + '  |  ' + ('%-*s' % (15, str(axis_4_raw_position_resolver_motor)))  # \
    # + '  |  ' + ('%-*s' % (18, str(axis_1_enc_position_resolver_motor)))\
    # + '  |  ' + ('%-*s' % (37, str(res)))\
    # + '  |  ' + ('%-*s' % (5, str(n_full_ecat))) + '  |  ' + ('%*s' % (4, str(n_ext)))
    print(rec)

    f = open('4_axe_rec.txt', 'a')
    f.write(rec + '\n')

