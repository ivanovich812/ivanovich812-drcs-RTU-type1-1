import os
import sys
from time import sleep
sys.path.append('../')

from logger import Logger
from configurator import Configurator
from client_rtu import ClientRtu
from data_model import DataModel
from SQL.sql_client import SQLClient
from controller import Controller
from datetime import datetime as dt, datetime


def main():
    config_path_com_a = os.path.join('../SYS_DATA', 'rtu_protocol_com_a.ini')
    config_path_com_b = os.path.join('../SYS_DATA', 'rtu_protocol_com_b.ini')
    logger = Logger()
    sql_client_com_a = SQLClient(logger, name='modbus_rtu_com_a')
    sql_client_com_b = SQLClient(logger, name='modbus_rtu_com_b')
    config_com_a = Configurator(config_path_com_a, logger)
    config_com_b = Configurator(config_path_com_b, logger)
    model_com_a = DataModel(sql_client_com_a)
    model_com_b = DataModel(sql_client_com_b)
    client_rtu_com_a= ClientRtu(config_com_a, logger, model_com_a)
    client_rtu_com_b = ClientRtu(config_com_b, logger, model_com_b)
    controller_rtu = Controller(client_rtu_com_a, client_rtu_com_b)
    # controller_rtu = Controller(client_rtu_com_a)


    while True:
        try:
            sleep(0.1)
        except KeyboardInterrupt:
            sys.exit(0)


if __name__ == '__main__':
    main()
