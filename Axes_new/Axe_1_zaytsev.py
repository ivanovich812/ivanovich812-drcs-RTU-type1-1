"""
Тестировали:

Не работает. Слишком большая погрешность при расчете угла только на основе показаний внешнего резольвера.
Нужно расчитывать учитывая показания резольвера мотора. Дима Зайцев занимался формулой. Не успели закончить.
"""

import sys
import os
from rtuGUI.file_hadlers import read_json
from time import sleep

# def convert_360(raw_0, raw_x, angle_0, angle_x):
#     delta_raw = raw_x - raw_0
#     delta_angle = angle_x - angle_0
#
#     angle = (4096 * delta_angle) / delta_raw
#
#     return  angle


def convert_angle_resolver(raw_value, raw_shift):

    # приводим значение в диапазоне от 0 до 4096 к 0 до 360 градусов
    max_raw_val = 4096

    if raw_value < raw_shift:
        raw_value = max_raw_val + (raw_value - raw_shift)
    else:
        raw_value = raw_value - raw_shift

    angle = (360 * raw_value) / 4096
    return angle


if __name__ == '__main__':

    data_plc_path = "../DATA_SRV/PLC/plc_io_monitor.json"
    axes_data_path = "../DATA_SRV/AXES/fc_axes_monitor.json"

    data_plc = read_json(data_plc_path)
    axes_data = read_json(axes_data_path)

    raw_position_1_ext = data_plc["raw_position_1_ext"]
    axis_1_raw_position_resolver_motor = axes_data["raw_position_resolver_motor"]["axis_1_raw_position_resolver_motor"]

    axis_1_actual_position = axes_data["actual_position"]["axis_1_actual_position"]

    raw_value = raw_position_1_ext
    raw_shift = 1356


    # conv_360 = convert_360(2, 1347, 134.19546913522817, 0.0)

    ang_calc = abs(convert_angle_resolver(raw_value, raw_shift) - 360) / 0.888888888888888888
    print (ang_calc)

    print('Погрешность: ', axis_1_actual_position - ang_calc)

    if abs(axis_1_actual_position - ang_calc) < 0.04:
        print ('Ok')
    else:
        print('No')