import os
import sys
from time import sleep

sys.path.append('../')

from logger import Logger
from configurator import Configurator
# from json_handler import JsonHandler # класс JsonHandler удален за ненадобностью
from client_plc import ClientPlc
from data_model import DataModel
from SQL.sql_client import SQLClient
from datetime import datetime as dt, datetime


def main():
    config_path = os.path.join('../SYS_DATA', 'plc_protocol.ini')
    plc_json_dir_path = os.path.join('../DATA_SRV', 'PLC')

    logger = Logger()
    sql_client = SQLClient(logger, name='plc-monitor')
    config = Configurator(config_path, logger)
    # json_handler = JsonHandler(plc_json_dir_path)
    model = DataModel(sql_client)
    client_plc = ClientPlc(config, logger, model)
    while True:
        try:
            client_plc.read_data()
            sleep(0.01)
            client_plc.write_data()
            sleep(0.01)
        except KeyboardInterrupt:
            sys.exit(0)


if __name__ == '__main__':
    main()
