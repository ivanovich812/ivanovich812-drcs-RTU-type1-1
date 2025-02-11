import struct

import snap7

plc = snap7.client.Client()
plc.connect('192.168.101.101', 0, 1)

# bool_signals
_bytes = plc.db_read(db_number=1, start=6, size=32)
# value = snap7.util.get_bool(_bytes, byte_index=2, bool_index=1)
print(_bytes)

# raw_position_ext
unpacked_reg = struct.unpack(">LLLL LLLL", _bytes)
print(unpacked_reg)
