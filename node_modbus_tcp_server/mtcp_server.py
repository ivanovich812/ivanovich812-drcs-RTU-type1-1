"""
rw функции не универсальны, сейчас в rw-функциях явно прописано в какую таблицу SQL она пишет
(аргумент path уже не передается в запись, как с json) быть внимательнее с этим!
"""

import os
import sys
sys.path.append('../')

from pyModbusTCP.server import ModbusServer
from time import sleep
from SQL.sql_client import SQLClient
from mdb_functions import *
from logger import Logger
from config import Configurator

"""
++++++++++++++++++++++++++++++++++++++++++++++++++++
Опрос/запись данных по Modbus TCP через SQL.
++++++++++++++++++++++++++++++++++++++++++++++++++++
Запись возможна, как с нижнего, так и с верхнего уровня.
Для добавления var к опросу:
- в параметрах ModbusServer("127.0.0.1", 502, no_block=True) выставить ip address (127.0.0.1 - если локально, 192.168.100.101 - если в локальной сети) и используемый порт (в Linux низкие номера
портов привелегерованные, поэтому можно использовать н.п. 1025)
- добавить путь к таблицу в список tables,
- если r/w опрос, добавить соотвеотствующую переменную с префиксом old_, как список с соответ.кол-м регистров, если просто чтение, то не надо.
- в ОПРОС добавить выполнение подходящей функции, учитывать кол-во используемых функцией регистров (1, 2 или 4) и структуру файла.
- при r/w опросе использовать форму old_var = func() 
"""


def main():

    logger = Logger()
    sql_client = SQLClient(logger, name='modbus_tcp_server')
    configurator = Configurator('parameters.json')

    tables = {
        "plc_io_monitor",
        "plc_tasks",
        "joint_points",
        "fc_axes_monitor",
        "rtc_control"
    }

    status_int_1 = 0

    # Old_vars (only for w/r)
    old_out_gripper_1_1 = False
    old_out_gripper_1_2 = False
    old_out_ready = False
    old_out_gripper_2345 = False
    old_out_enable_work = False

    old_rtc_sub_work_widget_index = [0, 0]
    old_subprocess_num = [0, 0]
    old_rtc_cmd_status = [0, 0]
    old_rtc_speed_value = [0, 0]
    old_rtc_joint_number = [0, 0]

    old_rtc_trajectory_btn_run = False
    old_rtc_trajectory_btn_check = False
    old_rtc_btn_enable = False
    old_rtc_btn_jog_cw = False
    old_rtc_btn_jog_ccw = False

    # old_zeros_0 = [0, 0, 0, 0]
    # old_zeros_1 = [0, 0, 0, 0]
    # old_zeros_2 = [0, 0, 0, 0]
    # old_zeros_3 = [0, 0, 0, 0]
    # old_zeros_4 = [0, 0, 0, 0]
    # old_zeros_5 = [0, 0, 0, 0]

    old_home_0 = [0, 0, 0, 0]
    old_home_1 = [0, 0, 0, 0]
    old_home_2 = [0, 0, 0, 0]
    old_home_3 = [0, 0, 0, 0]
    old_home_4 = [0, 0, 0, 0]
    old_home_5 = [0, 0, 0, 0]

    client = configurator.get_value('client')
    host = configurator.get_value('host')
    port = configurator.get_value('port') # Linux. Низкие номера портов такие как 502(по умолчанию) -привелегированные

    # Проверяем в сети ли клиент
    ping = os.system("ping -c 1 " + client)
    if ping == 0:
        host = host
    else:
        host = "127.0.0.1"
    # Create an instance of ModbusServer
    server = ModbusServer(host, port, no_block=True)
    logger.event('debug', f"ModbusTCP: Trying to start server {host}:{port}...")

    try:
        server.start()
    except:
        sys.exit(0)
        logger.event('error', "ModbusTCP: Error during Start server ...")
        server.stop()
        logger.event('debug', "ModbusTCP: Server is offline!")

    logger.event('debug', "ModbusTCP: Server is online!")

    while True:
        try:
            data = {}

            for key in tables:
                if key == "plc_io_monitor":
                    data[key] = sql_client.read_plc_io_monitor()
                elif key == "plc_tasks":
                    data[key] = sql_client.read_plc_tasks()
                elif key == "joint_points":
                    data[key] = sql_client.read_j_points()
                elif key == "fc_axes_monitor":
                    data[key] = sql_client.read_fc_axes_monitor()
                elif key == "rtc_control":
                    data[key] = sql_client.read_rtc_control()
                else:
                    print ("There isn't such table in database!")

            remote_enable = not data["plc_io_monitor"]["in_manual_mode"]


            # ОПРОС/ЗАПИСЬ
            # 1 modbus func (w/r)===============================================================
            if remote_enable:
                old_out_gripper_1_1 = rw_0x01_bool_plc_tasks(server, sql_client, data, "plc_tasks", "out_gripper_1_1", old_out_gripper_1_1, 10000)
                old_out_gripper_1_2 = rw_0x01_bool_plc_tasks(server, sql_client, data, "plc_tasks", "out_gripper_1_2", old_out_gripper_1_2, 10001)
                old_out_ready = rw_0x01_bool_plc_tasks(server, sql_client, data, "plc_tasks", "out_ready", old_out_ready, 10002)
                old_out_gripper_2345 = rw_0x01_bool_plc_tasks(server, sql_client, data, "plc_tasks", "out_gripper_2345", old_out_gripper_2345, 10003)
                old_out_enable_work = rw_0x01_bool_plc_tasks(server, sql_client, data, "plc_tasks", "out_enable_work", old_out_enable_work, 10004)

            # 1 modbus func (w/r)===============================================================
            if remote_enable:
                old_rtc_trajectory_btn_run = rw_0x01_bool_rtc_control(server, sql_client, data, "rtc_control", "rtc_trajectory_btn_run", old_rtc_trajectory_btn_run, 10100)
                old_rtc_trajectory_btn_check = rw_0x01_bool_rtc_control(server, sql_client, data, "rtc_control", "rtc_trajectory_btn_check", old_rtc_trajectory_btn_check, 10101)
                old_rtc_btn_enable = rw_0x01_bool_rtc_control(server, sql_client, data, "rtc_control", "rtc_btn_enable", old_rtc_btn_enable, 10102)
                old_rtc_btn_jog_cw = rw_0x01_bool_rtc_control(server, sql_client, data, "rtc_control", "rtc_btn_jog_cw", old_rtc_btn_jog_cw, 10103)
                old_rtc_btn_jog_ccw = rw_0x01_bool_rtc_control(server, sql_client, data, "rtc_control", "rtc_btn_jog_ccw", old_rtc_btn_jog_ccw, 10104)


            # 4 modbus func (only read)==========================================================
            status_int_1 = set_bit(data, 'plc_io_monitor', 'in_qf2_switched_on', status_int_1, 0)
            status_int_1 = set_bit(data, 'plc_io_monitor', 'in_qf3_switched_on', status_int_1, 1)
            status_int_1 = set_bit(data, 'plc_io_monitor', 'in_qf4_switched_on', status_int_1, 2)
            status_int_1 = set_bit(data, 'plc_io_monitor', 'in_qf5_switched_on', status_int_1, 3)
            status_int_1 = set_bit(data, 'plc_io_monitor', 'in_qf8_switched_on', status_int_1, 4)
            status_int_1 = set_bit(data, 'plc_io_monitor', 'in_qf7_switched_on', status_int_1, 5)
            status_int_1 = set_bit(data, 'plc_io_monitor', 'in_km1_switched_on', status_int_1, 6)
            status_int_1 = set_bit(data, 'plc_io_monitor', 'in_km2_switched_on', status_int_1, 7)
            status_int_1 = set_bit(data, 'plc_io_monitor', 'in_r1_overheat', status_int_1, 8)
            status_int_1 = set_bit(data, 'plc_io_monitor', 'in_screwdriver_1_on', status_int_1, 9)
            status_int_1 = set_bit(data, 'plc_io_monitor', 'in_screwdriver_2_on', status_int_1, 10)
            status_int_1 = set_bit(data, 'plc_io_monitor', 'in_multitool_1_on', status_int_1, 11)
            status_int_1 = set_bit(data, 'plc_io_monitor', 'in_multitool_2_on', status_int_1, 12)
            status_int_1 = set_bit(data, 'plc_io_monitor', 'in_emergency_stop', status_int_1, 13)
            status_int_1 = set_bit(data, 'plc_io_monitor', 'in_manual_mode', status_int_1, 14)
            status_int_1 = set_bit(data, 'plc_io_monitor', 'in_reset', status_int_1, 15)
            status_int_1 = set_bit(data, 'plc_io_monitor', 'in_cabinet_door_opened', status_int_1, 16)
            status_int_1 = set_bit(data, 'plc_io_monitor', 'in_cabinet_overheat', status_int_1, 17)
            status_int_1 = set_bit(data, 'plc_io_monitor', 'out_gripper_1_1', status_int_1, 18)
            status_int_1 = set_bit(data, 'plc_io_monitor', 'out_gripper_1_2', status_int_1, 19)
            status_int_1 = set_bit(data, 'plc_io_monitor', 'out_ready', status_int_1, 20)
            status_int_1 = set_bit(data, 'plc_io_monitor', 'out_gripper_2345', status_int_1, 21)
            status_int_1 = set_bit(data, 'plc_io_monitor', 'out_enable_work', status_int_1, 22)

            r_0x04_int32_status_int(server, status_int_1, 20000)

            # 3 modbus func (w/r)================================================================
            # old_zeros_0 = rw_0x03_double64_lst(server, sql_client, data, "joint_points", "zeros", 0, old_zeros_0, 30000)
            # old_zeros_1 = rw_0x03_double64_lst(server, sql_client, data, "joint_points", "zeros", 1, old_zeros_1, 30004)
            # old_zeros_2 = rw_0x03_double64_lst(server, sql_client, data, "joint_points", "zeros", 2, old_zeros_2, 30008)
            # old_zeros_3 = rw_0x03_double64_lst(server, sql_client, data, "joint_points", "zeros", 3, old_zeros_3, 30012)
            # old_zeros_4 = rw_0x03_double64_lst(server, sql_client, data, "joint_points", "zeros", 4, old_zeros_4, 30016)
            # old_zeros_5 = rw_0x03_double64_lst(server, sql_client, data, "joint_points", "zeros", 5, old_zeros_5, 30020)

            # old_home_0 = rw_0x03_double64_lst(server, sql_client, data, "joint_points", "home", 0, old_home_0, 30024)
            # old_home_1 = rw_0x03_double64_lst(server, sql_client, data, "joint_points", "home", 1, old_home_1, 30028)
            # old_home_2 = rw_0x03_double64_lst(server, sql_client, data, "joint_points", "home", 2, old_home_2, 30032)
            # old_home_3 = rw_0x03_double64_lst(server, sql_client, data, "joint_points", "home", 3, old_home_3, 30036)
            # old_home_4 = rw_0x03_double64_lst(server, sql_client, data, "joint_points", "home", 4, old_home_4, 30040)
            # old_home_5 = rw_0x03_double64_lst(server, sql_client, data, "joint_points", "home", 5, old_home_5, 30044)

            # 3 modbus func (w/r)===========================================================
            if remote_enable:
                old_rtc_sub_work_widget_index = rw_0x03_int32_rtc_control(server, sql_client, data, "rtc_control", "rtc_sub_work_widget_index", old_rtc_sub_work_widget_index, 30100)
                old_rtc_joint_number = rw_0x03_int32_rtc_control(server, sql_client, data, "rtc_control", "rtc_joint_number", old_rtc_joint_number, 30102)
                old_subprocess_num = rw_0x03_int32_rtc_control(server, sql_client, data, "rtc_control", "subprocess_num", old_subprocess_num, 30104)
                old_rtc_speed_value = rw_0x03_int32_rtc_control(server, sql_client, data, "rtc_control", "rtc_speed_value", old_rtc_speed_value, 30108)
            old_rtc_cmd_status = rw_0x03_int32_rtc_control(server, sql_client, data, "rtc_control", "rtc_cmd_status", old_rtc_cmd_status, 30106)

            # 4 modbus func (only read)===========================================================
            r_0x04_double64_dict(server, data, "fc_axes_monitor", "actual_speed", "axis_1_actual_speed", 40000)
            r_0x04_double64_dict(server, data, "fc_axes_monitor", "actual_speed", "axis_2_actual_speed", 40004)
            r_0x04_double64_dict(server, data, "fc_axes_monitor", "actual_speed", "axis_3_actual_speed", 40008)
            r_0x04_double64_dict(server, data, "fc_axes_monitor", "actual_speed", "axis_4_actual_speed", 40012)
            r_0x04_double64_dict(server, data, "fc_axes_monitor", "actual_speed", "axis_5_actual_speed", 40016)
            r_0x04_double64_dict(server, data, "fc_axes_monitor", "actual_speed", "axis_6_actual_speed", 40020)

            r_0x04_double64_dict(server, data, "fc_axes_monitor", "setpoint_speed", "axis_1_setpoint_speed", 40024)
            r_0x04_double64_dict(server, data, "fc_axes_monitor", "setpoint_speed", "axis_2_setpoint_speed", 40028)
            r_0x04_double64_dict(server, data, "fc_axes_monitor", "setpoint_speed", "axis_3_setpoint_speed", 40032)
            r_0x04_double64_dict(server, data, "fc_axes_monitor", "setpoint_speed", "axis_4_setpoint_speed", 40036)
            r_0x04_double64_dict(server, data, "fc_axes_monitor", "setpoint_speed", "axis_5_setpoint_speed", 40040)
            r_0x04_double64_dict(server, data, "fc_axes_monitor", "setpoint_speed", "axis_6_setpoint_speed", 40044)

            r_0x04_double64_dict(server, data, "fc_axes_monitor", "actual_position", "axis_1_actual_position", 40048)
            r_0x04_double64_dict(server, data, "fc_axes_monitor", "actual_position", "axis_2_actual_position", 40052)
            r_0x04_double64_dict(server, data, "fc_axes_monitor", "actual_position", "axis_3_actual_position", 40056)
            r_0x04_double64_dict(server, data, "fc_axes_monitor", "actual_position", "axis_4_actual_position", 40060)
            r_0x04_double64_dict(server, data, "fc_axes_monitor", "actual_position", "axis_5_actual_position", 40064)
            r_0x04_double64_dict(server, data, "fc_axes_monitor", "actual_position", "axis_6_actual_position", 40068)

            sleep(0.1)

        except KeyboardInterrupt:
            sys.exit(0)
            logger.event('debug', "ModbusTCP: Shutdown server ...")
            server.stop()
            logger.event('debug', "ModbusTCP: Server is offline!")

if __name__ == '__main__':
    main()