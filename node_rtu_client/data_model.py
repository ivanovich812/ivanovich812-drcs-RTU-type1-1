import numpy as np


class DataModel:
    def __init__(self, database):
        self.db = database
        self.signals = {}
        self.scope_signals = {}
        self.data = None

    def update_model(self, signals):
        self.db.write_mdbrtu_io_monitor(signals)

    def update_task_model(self, sinals):
        self.db.write_mdbrtu_tasks(sinals)

    def get_from_db(self):
        data = self.db.read_mdbrtu_tasks()
        if data is not None:
            self.data = data
            return data
        else:
            return self.data

