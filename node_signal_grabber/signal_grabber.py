import json
import os
import sys
from time import sleep

sys.path.append('../')


# from plc_grabber import read_json
# from fc_grabber import read_json
from fc_grabber import _prepare_data
# from SQL.sql_client import SQLClient
from SQL.sql_client import SQLClient

from logger import Logger


def main():

    logger = Logger()
    sql_client = SQLClient(logger, name='scope')
    # signals_file = '../DATA_SRV/SCOPE/signals.json'
    # file = None

    # if os.path.exists(signals_file):
    while True:
        try:
            # data_1 = read_json('../DATA_SRV/PLC/plc_io_monitor.json')
            # print('data_1: ', data_1)

            data_1 = sql_client.read_plc_io_monitor()
            # print('plc: ', data_1)

            # data_2 = read_json('../DATA_SRV/AXES/fc_axes_monitor.json')
            # print('data_2: ', data_2)

            data_2 = sql_client.read_fc_axes_monitor()
            data_2 = _prepare_data(data_2)
            # print('fc: ', data_2)

            data_1.update(data_2)
            # print('plc+fc: ', data_1)

            # with open(signals_file, 'w') as file:
            #     json.dump(data_1, file, indent=4, sort_keys=False)
                # print(data_1)

            sql_client.write_scope_signals(data_1)

            sleep(0.1)

        except KeyboardInterrupt:
            # file.close()
            sys.exit(0)


if __name__ == '__main__':
    main()
