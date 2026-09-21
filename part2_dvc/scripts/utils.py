import yaml


def load_params(path: str = "params.yaml") -> dict:
    """
    Загрузка гиперпараметров DVS.

    :param path: Путь до файла с гиперпараметрами.

    :return: Словарь с загруженными гиперпараметрами.
    """
    with open(path, "r") as f:
        return yaml.safe_load(f)
