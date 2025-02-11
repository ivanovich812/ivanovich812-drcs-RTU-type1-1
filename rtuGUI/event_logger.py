import logging
import time
import os
from logging.handlers import RotatingFileHandler
from PyQt5.QtCore import pyqtSignal, QObject


class Handler(QObject, logging.Handler):
    new_record = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        super(logging.Handler).__init__()

    def emit(self, record):
        msg = self.format(record)
        self.new_record.emit(msg)


class Formatter(logging.Formatter):

    def formatException(self, ei):
        result = super(Formatter, self).formatException(ei)
        return result

    def format(self, record):
        s = super(Formatter, self).format(record)
        if record.exc_text:
            s = s.replace('\n', '')
        return s


name = time.strftime("%Y-%m-%d_%H-%M-%S")
log_path = os.path.join('gui_log')
if not os.path.exists(log_path):
    os.umask(0) #разрешить доступ к создаваемой папке
    os.makedirs(log_path)

logger = logging.getLogger("SCADA")
handler = Handler()
handler_1 = RotatingFileHandler(os.path.join(log_path, f'{name}.log'), maxBytes=500000, backupCount=0)
handler.setFormatter(Formatter('%(levelname)s %(asctime)s %(message)s', '%d/%m/%Y %H:%M:%S'))
handler_1.setFormatter(Formatter('%(levelname)s %(asctime)s %(message)s', '%d/%m/%Y %H:%M:%S'))
logger.addHandler(handler)
logger.addHandler(handler_1)


