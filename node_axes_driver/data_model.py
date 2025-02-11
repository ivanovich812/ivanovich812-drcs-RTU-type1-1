class DataModel:
    def __init__(self, json, database):

        self._json = json
        self.db = database

        self._signals = {}
        self._robot_parameters = {}

        self._read_robot_params()

    def _read_robot_params(self):
        data = self._json.read_json('robot_parameters.json')
        if data is not None:
            self._robot_parameters = data

    def add_parameters(self, parameters):
        for parameter in parameters:
            self._signals[parameter] = {}

    def update_model(self, key, sub_key, value):
        if sub_key in self._robot_parameters['n'].keys():
            # self._signals[key][sub_key] = float(value * (360/65536) / self._robot_parameters['n'][sub_key]) # gefran
            self._signals[key][sub_key] = float(value * (360 / 4096) / self._robot_parameters['n'][sub_key])  # sew movidrive
            # self._signals[key][sub_key] = (value / 100.0) / self._robot_parameters['n'][sub_key] * 360.0
            # self._update_scope(sub_key, (value / 100.0) / self._robot_parameters['n'][sub_key] * 360.0)
        else:
            # формируется словарь для записи в fc_axes_monitor
            self._signals[key][sub_key] = float(value)
            # this is Andrey comment! self._update_scope(sub_key, value)

        # print('self._signals: ', self._signals)
        # self._json.write_json(self._signals)
        # print(self._signals)
        # Здесь происходит зопись EtherCat регистров в  fc_axes_monitor
        # print('self._signals: ', self._signals)
        self.db.write_fc_axes_monitor(self._signals)

    def get_robot_parameters(self):
        return self._robot_parameters

    def get_signals(self):
        return self._signals

    def _update_scope(self, key, value):
        self._json.add_to_json(key, value)

    # пытался сделать калибровку последними значениями из базы данных
    def read_raw_position(self):
        data = self.db.read_fc_axes_monitor()
        if data is not None:
            raws = data.get('raw_position_resolver_motor', None)
            self._raw_position = list(map(int, raws.values()))
            return self._raw_position

