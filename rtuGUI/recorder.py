import time
import pandas as pd
import os
import json
from datetime import datetime as dt


class Recorder:

    def __init__(self, directory, list_signals):
        self.directory = directory

        self.recorded_data = {}
        self.current_time = 0
        self.start_time = int(round(time.time() * 1000))

        self.recorded_data['Time'] = []

        for signal in list_signals:
            self.recorded_data[signal] = []

    @staticmethod
    def _check_filepath(filepath):
        if not os.path.exists(filepath):
            os.makedirs(filepath)

    def _create_directory(self, directory_path):
        self._check_filepath(directory_path)

    @staticmethod
    def read_scope_signals(database):
        db = database
        try:
            data = db.read_scope_signals()
            return data
        except:
            return None
    # def read_json(path):
    #     if os.path.exists(path):
    #         with open(path) as json_file:
    #             try:
    #                 data = json.load(json_file)
    #                 return data
    #             except json.decoder.JSONDecodeError:
    #                 return None

    def record_data(self, key, value):
        print(f'add key={key} value={value}')
        if isinstance(value, bool):
            self.recorded_data[key].append(int(value))
        else:
            self.recorded_data[key].append(value)

    def add_timestamp(self):
        current_time = int(round(time.time() * 1000))
        print(current_time)
        self.recorded_data['Time'].append(current_time - self.start_time)

    def save_data(self):
        for key, value in self.recorded_data.items():
            print(f'key={key}, len: {len(value)}')

        self._create_directory(self.directory)

        filepath = os.path.join(self.directory, dt.now().strftime('%Y_%m_%d-%H_%M_%S') + '.csv')

        dataframe = pd.DataFrame.from_dict(self.recorded_data)
        dataframe = dataframe.fillna(method='ffill')
        dataframe.to_csv(filepath, index=False)
        print('=' * 30)
