import numpy as np


class DataModel:
    def __init__(self, database):
        self.db = database
        self.signals = {}
        self.scope_signals = {}
        self.data = None
        self.raw_data_1_ext = []
        self.raw_data_2_ext = []
        self.raw_data_3_ext = []
        self.raw_data_4_ext = []
        self.raw_data_5_ext = []
        self.raw_data_6_ext = []
        self.raw_data_7_ext = []
        self.raw_data_8_ext = []
        self.window = 10

    def fill_list(self, value, data):
        data.append(int(value))
        if len(data) > self.window:
            data.pop(0)
            return data
        else:
            return data

    def smoothed_average(self, raw_data_ext):
        smoothed = np.convolve(raw_data_ext, np.ones(self.window) / self.window, 'valid')
        value = int(smoothed)
        return value

    def update_model_2(self, signals):
        self.db.write_plc_io_monitor(signals)

    def update_model(self, key, value):
        if key == 'raw_position_1_ext':
            self.fill_list(value, self.raw_data_1_ext)
            if len(self.raw_data_1_ext) > (self.window - 1):
                value = self.smoothed_average(self.raw_data_1_ext)
        elif key == 'raw_position_2_ext':
            self.fill_list(value, self.raw_data_2_ext)
            if len(self.raw_data_2_ext) > (self.window - 1):
                value = self.smoothed_average(self.raw_data_2_ext)
        elif key == 'raw_position_3_ext':
            self.fill_list(value, self.raw_data_3_ext)
            if len(self.raw_data_3_ext) > (self.window - 1):
                value = self.smoothed_average(self.raw_data_3_ext)
        elif key == 'raw_position_4_ext':
            self.fill_list(value, self.raw_data_4_ext)
            if len(self.raw_data_4_ext) > (self.window - 1):
                value = self.smoothed_average(self.raw_data_4_ext)
        elif key == 'raw_position_5_ext':
            self.fill_list(value, self.raw_data_5_ext)
            if len(self.raw_data_5_ext) > (self.window - 1):
                value = self.smoothed_average(self.raw_data_5_ext)
        elif key == 'raw_position_6_ext':
            self.fill_list(value, self.raw_data_6_ext)
            if len(self.raw_data_6_ext) > (self.window - 1):
                value = self.smoothed_average(self.raw_data_6_ext)
        elif key == 'raw_position_7_ext':
            self.fill_list(value, self.raw_data_7_ext)
            if len(self.raw_data_7_ext) > (self.window - 1):
                value = self.smoothed_average(self.raw_data_7_ext)
        elif key == 'raw_position_8_ext':
            self.fill_list(value, self.raw_data_8_ext)
            if len(self.raw_data_8_ext) > (self.window - 1):
                value = self.smoothed_average(self.raw_data_8_ext)

        self.signals[key] = value
        self.db.write_plc_io_monitor(self.signals)

    def get_from_db(self):
        # data = self.json.read_json()
        data = self.db.read_plc_tasks()
        if data is not None:
            self.data = data
            return data
        else:
            return self.data

