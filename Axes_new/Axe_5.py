"""
Рабочий расчет. Для GEFRAN. Не протестирован.
"""

import sys
import os
from rtuGUI.file_hadlers import read_json
from time import sleep
from logger import Logger
sys.path.append('../')
from SQL.sql_client import SQLClient


logger = Logger()
sql_client = SQLClient(logger, name='axes_calculating')

def convert_angle_resolver(raw_value, raw_shift):
    max_raw_val = 4096

    if raw_value < raw_shift:
        raw_value = max_raw_val + (raw_value - raw_shift)
    else:
        raw_value = raw_value - raw_shift

    angle = (360 * raw_value) / 4096
    return angle

# def normalize_motor_resolver(raw_value):
#     val = raw_value
#     if val < 0:
#         val = (val + 2**32) / 1048576
#     else:
#         val = val / 1048576
#
#     return val

def normalize_motor_resolver(raw_value):
    k = 65536/4096
    val = raw_value/k

    return val

def ang_calc(a, b, c):  # компиляция всего

    a_num_teeth = 19
    b_num_teeth = 20
    c_num_teeth = 21

    full_reduction_ratio = 398.4

    turn = 360
    ab_backlog_deg = (turn / b_num_teeth) * (b_num_teeth - a_num_teeth)
    ac_backlog_deg = (turn / c_num_teeth) * (c_num_teeth - a_num_teeth)

    ab_deg = 0
    if a - b < 0:
        ab_deg = a - b + turn
    else:
        ab_deg = a - b

    ab_turn = ab_deg / ab_backlog_deg

    ac_deg = a - c
    if a - c < 0:
        ac_deg  += turn

    ac_turn_preceed = ac_deg / ac_backlog_deg
    # print("Предварительно в оборотах - ", ac_turn_preceed)

    ac_recovery_by_ac_turn_preceed = (ac_turn_preceed * turn) % turn
    # print("Восстановление угла по ac-", ac_recovery_by_ac_turn_preceed)

    is_more_half = False
    if abs(ac_recovery_by_ac_turn_preceed - a) > 100 and abs(ac_recovery_by_ac_turn_preceed - a) < 200:
        is_more_half = True
    # print("Пройдены первые 15 оборотов - ", is_more_15_turn)


    ac_turn = ac_turn_preceed
    if is_more_half:
        ac_turn += 10.5
    # print("Выполнено оборотов ac -", ac_turn)

    ac_full_turn_loop = ab_turn - ac_turn
    if (ab_turn - ac_turn) < -0.1:
        ac_full_turn_loop = ab_turn - ac_turn + b_num_teeth
    ac_full_turn_loop = round(ac_full_turn_loop,0)
    # print("Кол-во полных циклов -", ac_full_turn_loop)

    degr_integral = ((ac_full_turn_loop * c_num_teeth) +  ac_turn // 1) * turn + a
    # print("Итеграл угла -",degr_integral)

    reverse_recovery = turn * ac_full_turn_loop * c_num_teeth + ac_turn * turn
    # print("Востановление обратное - ", reverse_recovery)

    a_degr_result = degr_integral
    if (degr_integral - reverse_recovery > 100) or (degr_integral - reverse_recovery < -100):
        a_degr_result += turn
    # print("Результат по а -" ,a_degr_result)

    b_degr_result = a_degr_result * a_num_teeth/b_num_teeth

    return b_degr_result / full_reduction_ratio # - ((b_degr_result / full_reduction_ratio)


def ang_calc_raw(a_raw, motor_resolver_raw, c_raw):

    # Значения резольверов в положении робота, которое он всегда до калибровки будет считать нулем
    # (опр. экспериментально в крайнем положении оси).
    a_raw_shift = 3296  # координата начальная "0" резольвера 6
    motor_resolver_raw_home_pos = 1162663936  # координата начальная "0" ротора мотора по Ethercat
    c_raw_shift = 1462  # координата начальная "0" резольвера 5

    b_raw = normalize_motor_resolver(motor_resolver_raw)  # ротор мотора мотор
    b_raw_shift = normalize_motor_resolver(motor_resolver_raw_home_pos)

    a = round(convert_angle_resolver(a_raw, a_raw_shift), 5)
    b = round(convert_angle_resolver(b_raw, b_raw_shift), 5)
    c = round(convert_angle_resolver(c_raw, c_raw_shift), 5)

    print(a, b, c)

    return ang_calc(a, b, c)


if __name__ == '__main__':
    data_plc = sql_client.read_plc_io_monitor()
    axes_data = sql_client.read_fc_axes_monitor()

    raw_position_5_ext = data_plc["raw_position_5_ext"]
    raw_position_6_ext = data_plc["raw_position_6_ext"]
    axis_5_raw_position_resolver_motor = axes_data["raw_position_resolver_motor"]["axis_5_raw_position_resolver_motor"]

    axis_5_actual_position = axes_data["actual_position"]["axis_5_actual_position"]


    motor_resolver_raw = axis_5_raw_position_resolver_motor # координата текущая ротора мотора по EtherCat
    motor_resolver_raw_home_pos = 1162663936 # координата начальная "0" ротора мотора по Ethercat

    a_raw = raw_position_6_ext # 6 ext
    # b_raw = motor_resolver_raw # ротор мотора мотор
    b_raw = normalize_motor_resolver(motor_resolver_raw % 65536)  # ротор мотора мотор
    c_raw = raw_position_5_ext  # 5 ext
    a_raw_shift = 3296 # координата начальная "0" резольвера 7
    b_raw_shift = normalize_motor_resolver(motor_resolver_raw_home_pos)
    c_raw_shift = 1462# координата начальная "0" резольвера 8


    a = round(convert_angle_resolver(a_raw, a_raw_shift), 5)
    b = round(convert_angle_resolver(b_raw, b_raw_shift), 5)
    c = round(convert_angle_resolver(c_raw, c_raw_shift), 5)

    # Для локального расчета
    print(a, b, c)
    ang_calc = ang_calc(a, b, c)

    print(ang_calc)
    print('Погрешность: ', axis_5_actual_position - ang_calc)

    if abs(axis_5_actual_position - ang_calc) < 0.04:
        print ('Ok')
    else:
        print('No')

    # print(normalize_motor_resolver(-1686226944))
    # print(normalize_motor_resolver(-994359296))



    # print(ang_calc(210, 251, 312.5806451612898) * 240)











# def convert_angle_resolver(raw_value, raw_shift):
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
# def normalize_motor_resolver(raw_value):
#     val = raw_value
#     if val < 0:
#         val = (val + 2**32) / 1048576
#     else:
#         val = val / 1048576
#
#     return val
#
# def ang_calc(a, b, c):  # компиляция всего
#
#     a_num_teeth = 19
#     b_num_teeth = 20
#     c_num_teeth = 21
#
#     full_reduction_ratio = 398.4
#
#     turn = 360
#     ab_backlog_deg = (turn / b_num_teeth) * (b_num_teeth - a_num_teeth)
#     ac_backlog_deg = (turn / c_num_teeth) * (c_num_teeth - a_num_teeth)
#
#     ab_deg = 0
#     if a - b < 0:
#         ab_deg = a - b + turn
#     else:
#         ab_deg = a - b
#
#     ab_turn = ab_deg / ab_backlog_deg
#
#     ac_deg = a - c
#     if a - c < 0:
#         ac_deg  += turn
#
#     ac_turn_preceed = ac_deg / ac_backlog_deg
#     # print("Предварительно в оборотах - ", ac_turn_preceed)
#
#     ac_recovery_by_ac_turn_preceed = (ac_turn_preceed * turn) % turn
#     # print("Восстановление угла по ac-", ac_recovery_by_ac_turn_preceed)
#
#     is_more_half = False
#     if abs(ac_recovery_by_ac_turn_preceed - a) > 100 and abs(ac_recovery_by_ac_turn_preceed - a) < 200:
#         is_more_half = True
#     # print("Пройдены первые 15 оборотов - ", is_more_15_turn)
#
#
#     ac_turn = ac_turn_preceed
#     if is_more_half:
#         ac_turn += 10.5
#     # print("Выполнено оборотов ac -", ac_turn)
#
#     ac_full_turn_loop = ab_turn - ac_turn
#     if (ab_turn - ac_turn) < -0.1:
#         ac_full_turn_loop = ab_turn - ac_turn + b_num_teeth
#     ac_full_turn_loop = round(ac_full_turn_loop,0)
#     # print("Кол-во полных циклов -", ac_full_turn_loop)
#
#     degr_integral = ((ac_full_turn_loop * c_num_teeth) +  ac_turn // 1) * turn + a
#     # print("Итеграл угла -",degr_integral)
#
#     reverse_recovery = turn * ac_full_turn_loop * c_num_teeth + ac_turn * turn
#     # print("Востановление обратное - ", reverse_recovery)
#
#     a_degr_result = degr_integral
#     if (degr_integral - reverse_recovery > 100) or (degr_integral - reverse_recovery < -100):
#         a_degr_result += turn
#     # print("Результат по а -" ,a_degr_result)
#
#     b_degr_result = a_degr_result * a_num_teeth/b_num_teeth
#
#     return b_degr_result / full_reduction_ratio # - ((b_degr_result / full_reduction_ratio)
#
#
# def ang_calc_raw(a_raw, motor_resolver_raw, c_raw):
#
#     # Значения резольверов в положении робота, которое он всегда до калибровки будет считать нулем
#     # (опр. экспериментально в крайнем положении оси).
#     a_raw_shift = 3296  # координата начальная "0" резольвера 6
#     motor_resolver_raw_home_pos = 1162663936  # координата начальная "0" ротора мотора по Ethercat
#     c_raw_shift = 1462  # координата начальная "0" резольвера 5
#
#     b_raw = normalize_motor_resolver(motor_resolver_raw)  # ротор мотора мотор
#     b_raw_shift = normalize_motor_resolver(motor_resolver_raw_home_pos)
#
#     a = round(convert_angle_resolver(a_raw, a_raw_shift), 5)
#     b = round(convert_angle_resolver(b_raw, b_raw_shift), 5)
#     c = round(convert_angle_resolver(c_raw, c_raw_shift), 5)
#
#     print(a, b, c)
#
#     return ang_calc(a, b, c)
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
#     raw_position_5_ext = data_plc["raw_position_5_ext"]
#     raw_position_6_ext = data_plc["raw_position_6_ext"]
#     axis_5_raw_position_resolver_motor = axes_data["raw_position_resolver_motor"]["axis_5_raw_position_resolver_motor"]
#
#     axis_5_actual_position = axes_data["actual_position"]["axis_5_actual_position"]
#
#
#     motor_resolver_raw = axis_5_raw_position_resolver_motor # координата текущая ротора мотора по EtherCat
#     motor_resolver_raw_home_pos = 1162663936 # координата начальная "0" ротора мотора по Ethercat
#
#     a_raw = raw_position_6_ext # 6 ext
#     b_raw = normalize_motor_resolver(motor_resolver_raw) # ротор мотора мотор
#     c_raw = raw_position_5_ext  # 5 ext
#     a_raw_shift = 3296 # координата начальная "0" резольвера 7
#     b_raw_shift = normalize_motor_resolver(motor_resolver_raw_home_pos)
#     c_raw_shift = 1462# координата начальная "0" резольвера 8
#
#
#     a = round(convert_angle_resolver(a_raw, a_raw_shift), 5)
#     b = round(convert_angle_resolver(b_raw, b_raw_shift), 5)
#     c = round(convert_angle_resolver(c_raw, c_raw_shift), 5)
#
#     # Для локального расчета
#     print(a, b, c)
#     ang_calc = ang_calc(a, b, c)
#
#     print(ang_calc)
#     print('Погрешность: ', axis_5_actual_position - ang_calc)
#
#     if abs(axis_5_actual_position - ang_calc) < 0.04:
#         print ('Ok')
#     else:
#         print('No')
#
#     # print(normalize_motor_resolver(-1686226944))
#     # print(normalize_motor_resolver(-994359296))
#
#
#
#     # print(ang_calc(210, 251, 312.5806451612898) * 240)