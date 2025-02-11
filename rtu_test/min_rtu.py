#!/usr/bin/env python3
import struct
from struct import pack, unpack

import serial
import minimalmodbus
from time import sleep

client1 = minimalmodbus.Instrument('/dev/ttyS0', 3, debug=False)  # port name, slave address (in decimal)
client1.serial.baudrate = 9600  # baudrate
client1.serial.bytesize = 8
client1.serial.parity   = serial.PARITY_NONE
client1.serial.stopbits = 1
client1.serial.timeout  = 0.1      # seconds
client1.address         = 3        # this is the slave address number
client1.mode = minimalmodbus.MODE_RTU # rtu or ascii mode
client1.clear_buffers_before_each_transaction = True

#######################
# informations
# print(client1)
# print('RS-485 Configurations')
# print('Port:\t\t', client1.serial.port)
# print('Baudrate:\t', client1.serial.baudrate)
# print('Byte Size:\t', client1.serial.bytesize)
# print('Parity:\t\t', client1.serial.parity)
# print('Stopbits:\t', client1.serial.stopbits)
# print('Timeout:\t', client1.serial.timeout)
# print()

while True:
# READ
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# # type-H Read-Only (1,2,3,4,8,9,10)
#     var = client1.read_registers(
#         registeraddress = int('1301', 16),
#         number_of_registers = 1,
#         functioncode = 3)[0]
#     print("var: ", var)

 # # type-h Read-Only (5, 11, 12)
 #    var = client1.read_register(
 #        registeraddress = int('130D', 16),
 #        number_of_decimals=0,
 #        functioncode=3,
 #        signed=True
 #    )
 #    print("var: ", var)

# # type-h Read-Only (5, 11, 12) another variant
#     var = client1.read_registers(
#         registeraddress = int('1315', 16),
#         number_of_registers = 1,
#         functioncode = 3)
#     print("var: ", var)
#
#     packed_string_var = struct.pack("H", *tuple(var))
#     print('packed_string_var: ', packed_string_var)
#
#     unpacked_var = struct.unpack("h", packed_string_var)[0]
#     print('unpacked_var: ', unpacked_var)

# type-l Read-Only (6,7)
# var = client1.read_registers(
#     registeraddress = int('1152', 16),
#     number_of_registers = 2,
#     functioncode = 3)
# print("var: ", var)
#
# packed_string_var = struct.pack("HH", *tuple(var))
# print('packed_string_var: ', packed_string_var)
#
# unpacked_var = struct.unpack("l", packed_string_var)[0]
# print('unpacked_var: ', unpacked_var)


# Чтение Read-Only (c 1301(4865) по 130E(4878) регистр или всего 14 регистров)

    var = client1.read_registers(
        registeraddress = int('1000', 16), #(in decimal)
        number_of_registers = 13, #
        functioncode = 3)  # Registernumber, number of decimals

    packed_string_var = struct.pack("H H HH HH HH HH H H H", *tuple(var))
    print('packed_string_var: ', packed_string_var)

    unpacked_var = struct.unpack("=H h l L L l H H H", packed_string_var)[0]
    print('unpacked_var: ', unpacked_var)

    print("var: ", var)


# packed_string_var = struct.pack('H', *tuple(var))
# print(len(packed_string_var))
# print('packed_string_var: ', packed_string_var)
# # #
# unpacked_var = struct.unpack('H', packed_string_var)
# print('unpacked_var: ', unpacked_var)



# WRITE
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Basic (3, 6) l-data type
# client1.write_long(registeraddress=int('1008', 16),
#                    value=-33333333,
#                    signed=True,
#                    byteorder= 3,
#                    number_of_registers=2
#                    )

# # Basic (4, 5) L-data type
# client1.write_long(registeraddress=int('1006', 16),
#                    value=3,
#                    signed=False,
#                    byteorder= 3,
#                    number_of_registers=2
#                    )


# # Basic (1, 7, 8, 9) H-data type
# client1.write_register(
#     registeraddress=int('100B', 16),
#     value=int('0', 16),
#     number_of_decimals=0,
#     functioncode=16,
#     signed=False)

# #Basic (2) h-data-type
# client1.write_register(
#     registeraddress=int('1001', 16),
#     value=55,
#     number_of_decimals=0,
#     functioncode=16,
#     signed=True)


# #Basic write all registers
# data = [0, -10, -30000, 5000, 6000, -7000, 2, 0, 0]
#
# packed_string_var = struct.pack('H h l L L l H H H', *tuple(data))
# print(len(packed_string_var))
# print('packed_string_var: ', packed_string_var)
# # #
# unpacked_var = struct.unpack('H H HH HH HH HH H H H', packed_string_var)
#
# unpacked_var = list(unpacked_var)
# print('unpacked_var: ', unpacked_var)
#
# client1.write_registers(
#     registeraddress=int('1000', 16),
#     values=unpacked_var
# )
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~




# input_stats  = client1.read_register(125) # read single register 2bytes (16bit)
# print("input stats: {0:016b}".format(input_stats))

# client1.write_register(125, 0, number_of_decimals=0, functioncode=6)
# client1.write_register(int("0x007D", 0), 24, functioncode=6)

# client1.write_register(int("0x007D", 0), 16, functioncode=6)
# write_register(registeraddress, value, number_of_decimals=0, functioncode=16, signed=False)

# a = int('0000000000011000',2)
# print(a)



    sleep(0.5)


    client1.close_port_after_each_call = True