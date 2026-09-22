import os
import pickle

import pandas as pd
import yaml
from category_encoders import CatBoostEncoder
from catboost import CatBoostRegressor
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from .utils import load_params


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

    model = CatBoostRegressor(
        iterations=params["model"]["iterations"],
        learning_rate=params["model"]["learning_rate"],
        depth=params["model"]["depth"],
        loss_function=params["model"]["loss_function"],
        random_state=params["model"]["random_state"],
        verbose=params["model"]["verbose"],
    )

    return Pipeline(steps=[("preprocessor", preprocessor), ("model", model)])


def fit_model():
    """
    Обучение модели для решения регрессионной задачи прогнозирования стоимость недвижимости.

    Обучающий датасет считывается из data.train_path. Имя целевой переменной считывается из гиперпараметра data.target_col.
    Данные обученной модели сохраняются в data.model_path.

    :return: None.
    """
    # загрузка гиперпараметров:
    params = load_params()

    data_params = params["data"]
    train_path = data_params["train_path"]
    model_path = data_params["model_path"]
    target_col = data_params["target_col"]

    # загрузка обучающего датасета:
    train = pd.read_csv(train_path)
    X_tr = train.drop(columns=[target_col])
    y_tr = train[target_col]

    # обучение модели:
    pipeline = build_pipeline(params)
    pipeline.fit(X_tr, y_tr)

    # сохранение результатов:
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    with open(model_path, "wb") as f:
        pickle.dump(pipeline, f)


if __name__ == "__main__":
    fit_model()
