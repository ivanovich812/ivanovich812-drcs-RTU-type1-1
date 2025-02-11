import struct
import pyModbusTCP
from pyModbusTCP import utils

def set_bit(data, table_name, var_name, status_int, offset): # Запись бита в число
    val_bool = data[table_name][var_name]
    try:
        if val_bool:
            status_int = pyModbusTCP.utils.set_bit(status_int, offset)
        else:
            status_int = pyModbusTCP.utils.reset_bit(status_int, offset)
        return status_int
    except:
        print('Check the data type!')

def get_bit(val_int, offset): # Чтение бита из числа (32-бит)
    bit_lst = pyModbusTCP.utils.get_bits_from_int(val_int, val_size=32)
    return bit_lst[offset]

'''
!!!для обычного одномерного json файла!!!
1 function: read/write boolean.
-используется 1 регистр памяти
'''
def rw_0x01_bool_plc_tasks(server, sql_client, data, table_name, var_name, old_var, start_reg):
    try:
        var = data[table_name][var_name]
        if old_var != (server.data_bank.get_coils(start_reg, 1))[0]:
            var = (server.data_bank.get_coils(start_reg, 1))[0]
            sql_client.add_to_plc_tasks(var_name, var)

            old_var = var
        else:
            old_var = var
        lst_var = []
        lst_var.append(var)

    except Exception:
        old_var = False
        lst_var = []
        lst_var.append(old_var)
        print(f"mdb_tcp: There isn't such variable: '{var_name}' in the table: '{table_name}'")

    server.data_bank.set_coils(start_reg, lst_var)
    return old_var

def rw_0x01_bool_rtc_control(server, sql_client, data, table_name, var_name, old_var, start_reg):
    try:
        var = data[table_name][var_name]
        if old_var != (server.data_bank.get_coils(start_reg, 1))[0]:
            var = (server.data_bank.get_coils(start_reg, 1))[0]
            sql_client.add_to_rtc_control(var_name, var)

            old_var = var
        else:
            old_var = var
        lst_var = []
        lst_var.append(var)

    except Exception:
        old_var = False
        lst_var = []
        lst_var.append(old_var)
        sql_client.add_to_rtc_control(var_name, old_var)
        print(f"mdb_tcp: Added variable: '{var_name}' in the table: '{table_name}'")

    server.data_bank.set_coils(start_reg, lst_var)
    return old_var

'''
ПРОВЕРЕНО!!!
2 function: read boolean.
-только чтение
-используется 1 регистр памяти
'''
def r_0x02_bool(server, data, table_name, var_name, start_reg):
    try:
        var = data[table_name][var_name]
    except Exception:
        var = 0
        print(f"mdb_tcp: There isn't such variable: '{var_name}' in the table: '{table_name}'")
    lst_var = []
    lst_var.append(var)
    server.data_bank.set_discrete_inputs(start_reg, lst_var)

"""
!!!для обычного одномерного json файла!!!
3 function: read float64 by [0, 0, 0, 0]
-используется передача данных в 4 регистрах с помощью double только для чтения чисел с точкой.
-передачей с float (2 регистра) не удается добиться точной передачи данных
-использовать эту функцию для чтения точных float значений, которые нельзя записывать
-порядок байт network - big endian, Double HG FE DC BA
"""
def r_0x03_double64(server, data, table_name, var_name, start_reg):
    var = data[table_name][var_name]
    packed_var = list(struct.unpack("!HHHH", struct.pack("d", var)))
    server.data_bank.set_holding_registers(start_reg, packed_var)

"""
ПЕРЕДЕЛАТЬ ПОД SQL!!!
!!!для обычного одномерного json файла!!!
3 function: read/write int by [0, 0]
-используется передача данных в 2 регистрах с помощью int для чтения/записи чисел integer type.
-sighned
-использовать эту функцию для записи integer
-порядок байт Long CD AB
"""
def rw_0x03_int32_rtc_control(server, sql_client, data, table_name, var_name, old_var, start_reg):
    try:
        var = data[table_name][var_name]
        packed_var = list(struct.unpack("HH", struct.pack("i", var)))
        if old_var != server.data_bank.get_holding_registers(start_reg, 2):
            packed_var = server.data_bank.get_holding_registers(start_reg, 2)
            packed_string_var = struct.pack("HH", *tuple(packed_var))
            unpacked_var = struct.unpack("i", packed_string_var)[0]
            sql_client.add_to_rtc_control(var_name, unpacked_var)
            old_var = packed_var
        else:
            old_var = packed_var
    except Exception:
        old_var = 0
        packed_var = [0, 0]
        sql_client.add_to_rtc_control(var_name, old_var)
        print(f"mdb_tcp: Added new variable: '{var_name}' in the table: '{table_name}'")

    server.data_bank.set_holding_registers(start_reg, packed_var)
    return old_var

"""
ПЕРЕДЕЛАТЬ ПОД SQL!!!
!!!для обычного одномерного json файла!!!
3 function: read/write float64 by [0, 0, 0, 0]
-используется передача данных в 4 регистрах с помощью double для чтения/записи чисел с точкой.
-передачей с float (2 регистра) не удается добиться точной передачи данных
-использовать эту функцию для записи точных значений, н.п. join_points
-порядок байт - Double GH EF CD AB
"""
# def rw_0x03_double64(path_name, var_name, old_var, start_reg):
#     var = data[path_name][var_name]
#     packed_var = list(struct.unpack("HHHH", struct.pack("d", var)))
#     if old_var != server.data_bank.get_holding_registers(start_reg, 4):
#         packed_var = server.data_bank.get_holding_registers(start_reg, 4)
#         packed_string_var = struct.pack("HHHH", *tuple(packed_var))
#         unpacked_var = struct.unpack("d", packed_string_var)[0]
#         add_to_json(paths[path_name], var_name, unpacked_var)
#         old_var = packed_var
#     else:
#         old_var = packed_var
#         server.data_bank.set_holding_registers(start_reg, packed_var)
#
#     return old_var

"""
!!!ДЛЯ таблицы joint_points или ему подобной структурой, где value это list!!!
3 function: read/write float64 by [0, 0, 0, 0]
-используется передача данных в 4 регистрах с помощью double для чтения/записи чисел с точкой.
-передачей с float (2 регистра) не удается добиться точной передачи данных
-использовать эту функцию для записи точных значений, н.п. join_points
-порядок байт network - Double GH EF CD AB
"""
def rw_0x03_double64_lst(server, sql_client, data, table_name, var_name, num, old_var, start_reg):
    try:
        var = data[table_name][var_name][num]
        packed_var = list(struct.unpack("HHHH", struct.pack("d", var)))
        if old_var != server.data_bank.get_holding_registers(start_reg, 4):
            packed_var = server.data_bank.get_holding_registers(start_reg, 4)
            packed_string_var = struct.pack("HHHH", *tuple(packed_var))
            unpacked_var = struct.unpack("d", packed_string_var)[0]
            data[table_name][var_name][num] = unpacked_var
            sql_client.add_to_j_points(var_name, data[table_name][var_name])
            old_var = packed_var
        else:
            old_var = packed_var
    except Exception:
        old_var = 0
        packed_var = [0, 0, 0, 0]
        print(f"mdb_tcp: There isn't such variable: '{var_name}' in the table: '{table_name}'")

    server.data_bank.set_holding_registers(start_reg, packed_var)
    return old_var

"""
4 function: read float32 by [0, 0]
-используется передача данных в 2 регистрах для чтения чисел float32 type.
-sighned
-использовать эту функцию для чтения float(точность ограничена)
-порядок байт float CD AB
"""
def r_0x04_float32(server, data, table_name, var_name, start_reg):
    var = data[table_name][var_name]
    packed_var = list(struct.unpack("HH", struct.pack("f", var)))
    server.data_bank.set_input_registers(start_reg, packed_var)

"""
4 function: read int by [0, 0]
-используется передача данных в 2 регистрах с помощью int для чтения чисел integer type.
-sighned
-использовать эту функцию для чтения integer
-порядок байт Long CD AB
"""
def r_0x04_int32(server, data, table_name, var_name, start_reg):
    var = data[table_name][var_name]
    packed_var = list(struct.unpack("HH", struct.pack("i", var)))
    server.data_bank.set_input_registers(start_reg, packed_var)

"""
4 function: read float64 by [0, 0, 0, 0]
-используется передача данных в 4 регистрах с помощью double только для чтения чисел с точкой.
-передачей с float (2 регистра) не удается добиться точной передачи данных
-использовать эту функцию для чтения точных float значений, которые нельзя записывать
-порядок байт network - big endian, Double HG FE DC BA
"""
def r_0x04_double64_dict(server, data, table_name, var_name, var_key, start_reg):
    # print(data)
    try:
        var = data[table_name][var_name][var_key]
        # print(var)
        packed_var = list(struct.unpack("<HHHH", struct.pack("d", var)))
    except Exception:
        packed_var = [0, 0, 0, 0]
        print(f"mdb_tcp: There isn't such variable: '{var_name}' in the table: '{table_name}'")
    server.data_bank.set_input_registers(start_reg, packed_var)

"""
4 function: read int 
-для записи слова состояния (передача булевых значений с помощью 32-бит integer)
"""
def r_0x04_int32_status_int(server, status_var, start_reg):
    var = status_var
    packed_var = list(struct.unpack("HH", struct.pack("i", var)))
    server.data_bank.set_input_registers(start_reg, packed_var)



