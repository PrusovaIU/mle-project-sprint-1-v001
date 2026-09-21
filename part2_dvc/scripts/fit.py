import argparse
import os
import pickle
from pathlib import Path

import pandas as pd
import yaml
from category_encoders import CatBoostEncoder
from catboost import CatBoostRegressor
from sklearn.compose import ColumnTransformer
from sklearn.metrics import (
    mean_absolute_error,
    mean_absolute_percentage_error,
    r2_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def build_pipeline(params: dict) -> Pipeline:
    """
    Подготовка пайплайна для трансформации признаков и обучения модели CatBoostRegressor.

    :param params: Гиперпараметры DVC.

    :return: Созданный пайплайн.
    """
    numeric_features = [
        "build_year", "latitude", "longitude", "ceiling_height",
        "flats_count", "floors_total", "kitchen_area", "living_area",
        "rooms", "total_area",
    ]
    binary_features = ["has_elevator", "is_apartment", "studio"]
    categorical_features = ["building_type_int", "floor"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("binary", OneHotEncoder(drop="if_binary", sparse_output=False), binary_features),
            ("cat", CatBoostEncoder(cols=categorical_features), categorical_features),
            ("num", StandardScaler(), numeric_features),
        ],
        remainder="drop",
    )

    model_params = params["model"]

    model = CatBoostRegressor(
        iterations=model_params["iterations"],
        learning_rate=model_params["learning_rate"],
        depth=model_params["depth"],
        loss_function=model_params["loss_function"],
        random_state=model_params["random_state"],
        verbose=model_params["verbose"],
    )

    return Pipeline(steps=[("preprocessor", preprocessor), ("model", model)])


def model_eval(y_val: pandas.Series, y_pred: numpy.ndarray) -> None:
    """
    Оценка обученной модели по метрикам MAE, MAPE и R^2.

    :param y_val: целевая переменная из валидационного сета.
    :param y_pred: целевая переменная, предсказанная для валидационного сета.

    :return: None.
    """
    mae = mean_absolute_error(y_val, y_pred)
    mape = mean_absolute_percentage_error(y_val, y_pred) * 100
    r2 = r2_score(y_val, y_pred)
    print(f"MAE:  {mae:.2f}")
    print(f"MAPE: {mape:.2f}%")
    print(f"R^2:  {r2:.4f}")


def fit():
    """
    Обучение модели для решения регрессионной задачи прогнозирования стоимость недвижимости.

    Использует следующие гиперпараметры:

      - data.initial_data_path
      - data.model_path
      - split.test_size
      - split.random_state
      - model.iterations
      - model.learning_rate
      - model.depth
      - model.loss_function
      - model.random_state
      - model.verbose

    Обучающий датасет считывается из data.initial_data_path. 
    Данные обученной модели сохраняются в data.model_path.

    :return: None.
    """
    # загрузка гиперпараметров:
    with open('params.yaml', 'r') as fd:
        params = yaml.safe_load(fd)

    data_params = params["data"]
    data_path = data_params["initial_data_path"]
    model_path = data_params["model_path"]

    split_params = params["split"]
    test_size = split_params["test_size"]
    random_state = split_params["random_state"]

    # подготовка данных для обучения:
    data = pd.read_csv(data_path)
    X_tr, X_val, y_tr, y_val = train_test_split(
        data, data["price"],
        test_size=test_size,
        random_state=random_state,
    )

    # трансформация признаков и обучение:
    pipeline = build_pipeline(params)
    pipeline.fit(X_tr, y_tr)

    # обучение и оценка модели:
    y_pred = pipeline.predict(X_val)
    model_eval(y_val, y_pred)

    # сохранение данных:
    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    with open(model_path, "wb") as f:
        pickle.dump(pipeline, f)


if __name__ == "__main__":
    fit()
