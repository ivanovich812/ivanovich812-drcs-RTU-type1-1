"""
Моя функция. Проверял только на данных из WatsApp (переписка с Димой Зайцевым).
Рабочий расчет. Для GEFRAN. Не протестирован.
Тестить на роботе в реале. Если норм сделать аналогично для 2,3,4 осей.
"""

import math
import sys
import os
from rtuGUI.file_hadlers import read_json
from time import sleep
from logger import Logger
sys.path.append('../')
from SQL.sql_client import SQLClient


logger = Logger()
sql_client = SQLClient(logger, name='axes_calculating')

def normalize_motor_resolver(raw_value):
    k = 65536/4096
    val = raw_value/k
    return val

def convert_angle_resolver_motor(raw_value, raw_shift):

    # приводим значение в диапазоне от 0 до 4096 к 0 до 360 градусов
    max_raw_val = 360

    if raw_value < raw_shift:
        raw_value = max_raw_val + (raw_value - raw_shift)
    else:
        raw_value = raw_value - raw_shift

    angle = (360 * raw_value) / 360
    return angle

    # приводим значение в диапазоне от 0 до 4096 к 0 до 360 градусов
    # max_raw_val = 4096
    #
    # if raw_value < raw_shift:
    #     raw_value = max_raw_val + (raw_value - raw_shift)
    # else:
    #     raw_value = raw_value - raw_shift
    #
    # angle = (360 * raw_value) / 4096
    # return angle

def convert_angle_resolver(raw_value, raw_shift): # ПРОВЕРЕНО! Кол-во оборотов на 1_positiv.py считает правильно.

    # приводим значение в диапазоне от 0 до 4096 к 0 до 360 градусов
    max_raw_val = 4096

    if raw_value >= raw_shift:
        # raw_value = max_raw_val + (raw_value - raw_shift)
        raw_value = raw_value - raw_shift
    else:
        # raw_value = raw_value - raw_shift
        raw_value = max_raw_val + (raw_value - raw_shift)

    angle = (360 * raw_value) / 4096
    return angle

    # if raw_value <= raw_shift:
    #     # raw_value = max_raw_val + (raw_value - raw_shift)
    #     raw_value = raw_shift - raw_value
    # else:
    #     # raw_value = raw_value - raw_shift
    #     raw_value = max_raw_val - (raw_value - raw_shift)
    #
    # angle = (360 * raw_value) / 4096
    # return angle

# общая функция для импорта и использования в проекте
def ang_calc_raw(a_raw, motor_resolver_raw):

    raw_value = a_raw
    raw_shift = 3309

    raw_value_motor = normalize_motor_resolver(motor_resolver_raw)
    raw_shift_motor = normalize_motor_resolver(-6510)

    # значение после калибровки для корректировки (на первой оси не получается откалибровать точно в ноль)
    zero_shift = 0

    ang_calc_raw = abs(convert_angle_resolver(raw_value, raw_shift)) / 0.888888888888888888
    ang_calc_motor = abs(convert_angle_resolver_motor(raw_value_motor, raw_shift_motor))

    n = (ang_calc_raw/360)*386.946
    n_full = math.floor(n)

    ang_calc = (n_full*360 + ang_calc_motor)/386.946 + zero_shift

    return ang_calc


# для теста
if __name__ == '__main__':

    data_plc = sql_client.read_plc_io_monitor()
    axes_data = sql_client.read_fc_axes_monitor()

    raw_position_1_ext = data_plc["raw_position_1_ext"]
    axis_1_raw_position_resolver_motor = axes_data["raw_position_resolver_motor"]["axis_1_raw_position_resolver_motor"]
    axis_1_actual_position = axes_data["actual_position"]["axis_1_actual_position"]

    raw_value = raw_position_1_ext
    raw_shift = 3309

    # raw_value_motor = axis_1_raw_position_resolver_motor
    raw_value_motor = normalize_motor_resolver(axis_1_raw_position_resolver_motor)
    # raw_shift_motor = -779499520
    raw_shift_motor = normalize_motor_resolver(0)

    zero_shift = 0
    # zero_shift = -0.22328697027492206
    # ang_ecat = 1.3833490256271224
    # ang_ecat = 10.020002791087126

    ang_calc = abs(convert_angle_resolver(raw_value, raw_shift)) / 0.888888888888888888 #угол поворота 1 оси от нулевой точки смещения, согласно внешнему резольверу, градусы
    ang_calc_motor = abs(convert_angle_resolver_motor(raw_value_motor, raw_shift_motor))
    ang_calc_motor_Zaytzev = (axis_1_raw_position_resolver_motor % 65536)*(360/65536) # угол поворота мотора в пределах одного оборота, градусы
    ang_calc_xxx = ang_calc_motor/386.946 + zero_shift

    n_full = (ang_calc/360)*386.946
    n_full = math.floor(n_full)

    ang = (n_full*360 + ang_calc_motor)/386.946 + zero_shift

    # f = ang_ecat/ang

    print('raw_value:', raw_value)
    print('raw_shift', raw_shift)
    print('raw_value_motor: ', raw_value_motor)
    print('raw_shift_motor: ', raw_shift_motor)
    print('ang_calc_motor_Zaytzev: ', ang_calc_motor_Zaytzev)
    print ('ang_calc: ', ang_calc)
    print('ang_calc_xxx: ', ang_calc_xxx)
    print('ang_calc_motor: ', ang_calc_motor)
    print('n_full: ', n_full)
    # print('f: ', f)
    print('ANGLE: ', ang)

    print('Погрешность: ', axis_1_actual_position - ang_calc)

    if abs(axis_1_actual_position - ang_calc) < 0.04:
        print ('Ok')
    else:
        print('No')
























# def normalize_motor_resolver(raw_value):
#     val = raw_value
#     if val < 0:
#         val = (val + 2**32) / 1048576
#     else:
#         val = val / 1048576
#
#     return val
#
# def convert_angle_resolver_motor(raw_value, raw_shift):
#
#     # приводим значение в диапазоне от 0 до 4096 к 0 до 360 градусов
#     max_raw_val = 4096
#
#     if raw_value < raw_shift:
#         raw_value = max_raw_val + (raw_value - raw_shift)
#     else:
#         raw_value = raw_value - raw_shift
#
#     angle = (360 * raw_value) / 4096
#     return angle
#
# def convert_angle_resolver(raw_value, raw_shift):
#
#     # приводим значение в диапазоне от 0 до 4096 к 0 до 360 градусов
#     max_raw_val = 4096
#
#     if raw_value <= raw_shift:
#         # raw_value = max_raw_val + (raw_value - raw_shift)
#         raw_value = raw_shift - raw_value
#     else:
#         # raw_value = raw_value - raw_shift
#         raw_value = max_raw_val - (raw_value - raw_shift)
#
#     angle = (360 * raw_value) / 4096
#     return angle
#
# # общая функция для импорта
# def ang_calc_raw(a_raw, motor_resolver_raw):
#
#     raw_value = a_raw
#     raw_shift = 1356
#
#     raw_value_motor = normalize_motor_resolver(motor_resolver_raw)
#     raw_shift_motor = normalize_motor_resolver(-779499520)
#
#     # значение после калибровки для корректировки (на первой оси не получается откалибровать точно в ноль)
#     zero_shift = -0.22328697027492206
#
#     ang_calc_raw = abs(convert_angle_resolver(raw_value, raw_shift)) / 0.888888888888888888
#     ang_calc_motor = abs(convert_angle_resolver_motor(raw_value_motor, raw_shift_motor))
#
#     n = (ang_calc_raw/360)*386.946
#     n_full = math.floor(n)
#
#     ang_calc = (n_full*360 + ang_calc_motor)/386.946 + zero_shift
#
#     return ang_calc
#
#
#
# if __name__ == '__main__':
#
#     data_plc_path = "../DATA_SRV/PLC/plc_io_monitor.json"
#     axes_data_path = "../DATA_SRV/AXES/fc_axes_monitor.json"
#
#     data_plc = read_json(data_plc_path)
#     axes_data = read_json(axes_data_path)
#
#     raw_position_1_ext = data_plc["raw_position_1_ext"]
#     axis_1_raw_position_resolver_motor = axes_data["raw_position_resolver_motor"]["axis_1_raw_position_resolver_motor"]
#     axis_1_actual_position = axes_data["actual_position"]["axis_1_actual_position"]
#
#     raw_value = raw_position_1_ext
#     raw_shift = 1356
#
#     raw_value_motor = normalize_motor_resolver(axis_1_raw_position_resolver_motor)
#     raw_shift_motor = normalize_motor_resolver(-779499520)
#
#     zero_shift = -0.22328697027492206
#     ang_ecat = 10.020002791087126
#
#     ang_calc = abs(convert_angle_resolver(raw_value, raw_shift)) / 0.888888888888888888
#     ang_calc_motor = abs(convert_angle_resolver_motor(raw_value_motor, raw_shift_motor))
#     ang_calc_xxx = ang_calc_motor/386.946 + zero_shift
#
#     n_full = (ang_calc/360)*386.946
#     n_full = math.floor(n_full)
#
#     ang = (n_full*360 + ang_calc_motor)/386.946 + zero_shift
#
#     f = ang_ecat/ang
#
#     print('raw_value:', raw_value)
#     print('raw_shift', raw_shift)
#     print('raw_value_motor:', raw_value_motor)
#     print ('ang_calc: ', ang_calc)
#     print('ang_calc_xxx: ', ang_calc_xxx)
#     print('ang_calc_motor: ', ang_calc_motor)
#     print('n_full: ', n_full)
#     print('f: ', f)
#     print('ANGLE: ', ang)
#
#     # print('Погрешность: ', axis_1_actual_position - ang_calc)
#     #
#     # if abs(axis_1_actual_position - ang_calc) < 0.04:
#     #     print ('Ok')
#     # else:
#     #     print('No')