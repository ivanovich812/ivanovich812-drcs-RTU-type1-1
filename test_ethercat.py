import pysoem
from time import sleep
import struct
import numpy as np

from datetime import datetime

# id сетевого адаптера
name = 'eno1'


master = pysoem.Master()
a = pysoem.find_adapters()
print(a)

master.open(name)
master.config_init()
print(master.slaves)
device = master.slaves[0]
print(master.slaves, len(master.slaves))

# write_example
# "speed_positive_setpoint": [8377, 2, 0]
# device.sdo_write(value[0], value[1], (value[2]).to_bytes(4, 'little', signed=True))

# read_example
# data = slave.sdo_read(cmd[0], cmd[1])
# positions.append(int.from_bytes(data, 'little', signed=True))

# data = int.from_bytes(data, 'little', signed=True) CHECKED: read integer
# data = np.frombuffer(data, dtype=np.int32)[0] CHECKED: read integer
# data = np.frombuffer(data, dtype=np.float32)[0] CHECKED: read float

# value = np.array(value, dtype=np.float32).tobytes() CHECKED: write float
# device.sdo_write(10032 + offset, 0, value)

# value = np.array(value, dtype=np.int32).tobytes() CHECKED: write integer
# device.sdo_write(1452 + offset, 0, value)

# data = device.sdo_read(10048 + offset, 0) CHECKED: read enumerate
# data = np.frombuffer(data, dtype=np.int16)[0]

# value = np.array(value, dtype=np.int16).tobytes() CHECKED: write enumerate
# device.sdo_write(10048 + offset, 0, value)

# offset = 8192 # 0x2000

## WRITE ENUMERATE
## value = 2056
## value = np.array(value, dtype=np.uint16).tobytes()
## while True:
##     try:
##
##         device.sdo_write(10001 + offset, 0, value)
##
##
##
##     except Exception as e:
##         print({e})
##     sleep(1)


## WRITE ENUMERATE
## value = 4
## value = np.array(value, dtype=np.uint32).tobytes()
## while True:
##     try:
##         device.sdo_write(10000 + offset, 0, value)
##     except Exception as e:
##         print({e})
##     sleep(1)

# WRITE INTEGER (CoolDrive)
# value = 1
# value = np.array(value, dtype=np.uint8).tobytes()
# print(f'{value=}')
# while True:
#     try:
#         device.sdo_write(0x1C12, 0x0, value)
#     except Exception as e:
#         print({e})
#     sleep(1)

# READ INTEGER (CoolDrive)
while True:
    try:
        data = device.sdo_read(0x1600, 0x1)
        print(data)
        data = np.frombuffer(data, dtype=np.uint32)[0]
        print(data)
    except Exception as e:
        print({e})
    sleep(1)



# WRITE FLOAT 32
# value = 2.5.
# value = np.array(value, dtype=np.float32).tobytes()
# while True:
#     try:
#         device.sdo_write(10016 + offset, 0, value)
#     except Exception as e:
#         print({e})
#     sleep(1)

# READ FLOAT 32
# while True:
#     try:
#         data = device.sdo_read(1101 + offset, 0)
#         data = np.frombuffer(data, dtype=np.float32)[0]
#         print(data)
#     except Exception as e:
#         print({e})
#     sleep(1)

# TIME
# t1=datetime.now()
# print(t1)
# data = device.sdo_read(1101 + offset, 0)
# data = np.frombuffer(data, dtype=np.float32)[0]
# t2=datetime.now()
# print(t2)
# t = t2 - t1
# print("t: ", t)
# print(data)


# READ ENUMERATE
# while True:
#     try:
#         data = device.sdo_read(10048 + offset, 0)
#         data = np.frombuffer(data, dtype=np.int16)[0]
#
#         print(data)
#     except Exception as e:
#         print({e})
#     sleep(1)




# WRITE CONTROL WORD FROM 0 TO 65356
# value = 500
# data = 0
#
# while True:
    # WRITE
    # try:
    #     value = value
    #
    #     value_bytes = np.array(value, dtype=np.uint16).tobytes()
    #     t1=datetime.now()
    #     # print(t1)
    #     device.sdo_write(10001 + offset, 0, value_bytes)
    #     t2=datetime.now()
    #     # print(t2)
    #     t = t2 - t1
    #     # print('value:', value, t)
    #     print('value:', value)
    #     # print("t: ", t)
    #     # print(data)
    #     value += 1
    #
    #     sleep(0.5)
    # except Exception as e:
    #     print({e})
    # sleep(1)
    #
    # # READ
    #
    # try:
    #     data = device.sdo_read(14006 + offset, 0)
    #     data = np.frombuffer(data, dtype=np.uint16)[0]
    #     if data != 0:
    #         print(f'Data = {data} Value = {value}')
    # except Exception as e:
    #     print({e})
    # sleep(1)

## для комментирования строк ALT + 3
## для разкомментирования строк ALT + 4
