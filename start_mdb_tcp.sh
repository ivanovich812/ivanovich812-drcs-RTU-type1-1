#!/bin/bash

echo "START MODBUS-TCP SERVER..."
cd ../RTU-SEW/node_modbus_tcp_server
python3 mtcp_server.py
