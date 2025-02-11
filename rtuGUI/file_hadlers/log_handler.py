def read_from_log_file(path):
    with open(path, "r") as file:
        data = file.read()
        return str(data)