import os

import pandas as pd
import yaml
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine


def create_connection() -> Engine:
    """
    Создание подключения к БД с датасетом.
    Параметры подключения запрашиваются из файла .env:

    - DB_HOST
    - DB_PORT
    - DB_NAME
    - DB_USER
    - DB_PASSWORD

    :param sslmode: режим SSL для подключения к PostgreSQL.
    :return: новое подключение к БД.
    """
    load_dotenv()
    host = os.environ.get("DB_HOST")
    port = os.environ.get("DB_PORT")
    db = os.environ.get("DB_NAME")
    username = os.environ.get("DB_USER")
    password = os.environ.get("DB_PASSWORD")

    conn = create_engine(f"postgresql://{username}:{password}@{host}:{port}/{db}")
    return conn


def get_data():
    """
    Загрузка данных: данные выгружаются из БД и сохраняются в файл,
    указанный в params.yaml.

    В процессе выполнения задачи загружаются гиперпараметры:
    - table
    - output_path
    - sslmode
    """
    with open("params.yaml", "r") as fd:
        params = yaml.safe_load(fd)

    table = params["table"]
    output_path = params["output_path"]

    conn = create_connection()
    data = pd.read_sql(f"select * from {table}", conn)
    conn.dispose()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    data.to_csv(output_path, index=None)


if __name__ == "__main__":
    get_data()
