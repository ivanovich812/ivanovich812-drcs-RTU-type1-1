import os
from time import sleep
import sys
sys.path.append('../')

from configurator import Configurator
from json_handler import JsonHandler
from logger import Logger
from data_model import DataModel
from snap7_master import Client
from server import Server
from controller import Controller
from SQL.sql_client import SQLClient


def main():
    config_path = os.path.join('../SYS_DATA', 'axes_monitor_protocol.ini')
    axes_json_dir_path = os.path.join('../DATA_SRV', 'AXES')
    protocol_path = os.path.join('protocol.json')
    scope_dir_path = os.path.join('../DATA_SRV', 'SCOPE', 'signals.json')

    logger = Logger()
    config = Configurator(config_path, logger)
    json_handler = JsonHandler(axes_json_dir_path, scope_dir_path)
    sql_client = SQLClient(logger, name='axes_driver')
    data_model = DataModel(json_handler, sql_client)
    ecat_master = Client(config, logger, data_model, protocol_path, json_handler)
    server = Server(ecat_master, logger)
    controller_logic = Controller(ecat_master, server)

    while True:
        try:
            sleep(0.1)
        except KeyboardInterrupt:
            sys.exit(0)


if __name__ == '__main__':
    main()
