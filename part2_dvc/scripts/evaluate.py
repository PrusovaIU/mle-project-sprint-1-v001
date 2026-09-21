import json
import os
import pickle

import pandas as pd
import yaml
from sklearn.metrics import (
    mean_absolute_error,
    mean_absolute_percentage_error,
    median_absolute_error,
    r2_score,
)


def load_params(path: str = "params.yaml") -> dict:
    """
    Загрузка гиперпараметров DVS.

    :param path: Путь до файла с гиперпараметрами.

    :return: Словарь с загруженными гиперпараметрами.
    """
    with open(path, "r") as f:
        return yaml.safe_load(f)


def evaluate_model():
    # загрузка гиперпараметров:
    params = load_params()

    data_params = params["data"]
    val_path = data_params["val_path"]
    model_path = data_params["model_path"]
    target_col = data_params["target_col"]

    metrics_path = params["evaluate"]["metrics_path"]

    # загрузка обученной модели:
    with open(model_path, "rb") as f:
        model = pickle.load(f)

    # загрузка валидационного датасета:
    val = pd.read_csv(val_path)
    X_val = val.drop(columns=[target_col])
    y_val = val[target_col]

    # оценка модели:
    y_pred = model.predict(X_val)

    result = {
        "mae": round(mean_absolute_error(y_val, y_pred), 2),
        "mape": round(mean_absolute_percentage_error(y_val, y_pred) * 100, 2),
        "medae": round(median_absolute_error(y_val, y_pred), 2),
        "r2": round(r2_score(y_val, y_pred), 4),
    }

    # сохранение результатов
    os.makedirs(os.path.dirname(metrics_path), exist_ok=True)
    with open(metrics_path, "w") as f:
        json.dump(result, f, indent=4)

    print(f"Метрики сохранены {metrics_path}: {result}")


if __name__ == "__main__":
    evaluate_model()
