import os

import pandas as pd
import yaml
from sklearn.model_selection import GroupShuffleSplit, train_test_split
from .utils import load_params


def split_data() -> None:
    """
    Разделение датасета на обучающий и валидационный.

    Считывает датасет из файла, путь к которому прописан в гиперпараметре: data.initial_data_path.
    Записывает результат:
        - обучающую выборку в файл, путь к которому прописан в гиперпараметре data.train_path.
        - валидационную выборку в файл, путь к которому прописан в гиперпараметре data.val_path.
    """
    # загрузка гиперпараметров:
    params = load_params()

    data_params = params["data"]
    data_path = data_params["initial_data_path"]
    train_path = data_params["train_path"]
    val_path = data_params["val_path"]
    target_col = data_params["target_col"]

    split_params = params["split"]
    test_size = split_params["test_size"]
    random_state = split_params["random_state"]

    # загрузка данных:
    data = pd.read_csv(data_path)

    # разделение датасета:
    train_idx, val_idx = train_test_split(
        data.index, test_size=test_size, random_state=random_state
    )

    # сохранение результата:
    os.makedirs(os.path.dirname(train_path), exist_ok=True)
    data.loc[train_idx].to_csv(train_path, index=None)
    data.loc[val_idx].to_csv(val_path, index=None)


if __name__ == "__main__":
    split_data()
