import os


def write_to_txt_file(data, path, filename):
    if not os.path.exists(path):
        os.umask(0)  # разрешить доступ к создаваемой папке
        os.mkdir(path)

    path = os.path.join(path, filename)
    with open(f"{path}.txt", "w") as file:
        file.write(data)

def read_from_txt_file(path, filename):
        path = os.path.join(path, filename)
        with open(path, "r") as file:
            data = file.read()
            return str(data)

def delete_txt_file(path, filename):
    path = os.path.join(path, filename)
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
