import csv
import numpy as np


def read_csv(filepath):
    _raw_data = []
    try:
        with open(filepath, 'r') as file:
            reader = csv.reader(file, delimiter=',')
            for row in reader:
                _raw_data.append(row)

        return _raw_data

    except Exception as e:
        print(e)


def pack_data(data):
    try:
        _headers = data[0]
        _values = np.column_stack(data[1:]).astype(np.float64).tolist()
        _data = {header: value for header, value in zip(_headers, _values)}
        return _data
    except Exception as e:
        print(e)
