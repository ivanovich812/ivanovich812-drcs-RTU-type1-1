#!/bin/bash

./start_axes.sh &
./start_plc.sh &
./start_scope.sh &
./start_gui.sh &
./start_mdb_rtu.sh &
./start_mdb_tcp.sh
