import os

import pandas as pd
import yaml
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine


def create_connection(sslmode: str = "require") -> Engine:
    """
    Создание подключения к БД с датасетом.
    Параметры подключения запрашиваются из файла .env:

    - DB_DESTINATION_HOST
    - DB_DESTINATION_PORT
    - DB_DESTINATION_NAME
    - DB_DESTINATION_USER
    - DB_DESTINATION_PASSWORD

    :param sslmode: режим SSL для подключения к PostgreSQL.
    :return: новое подключение к БД.
    """
    load_dotenv()
    host = os.environ.get("DB_DESTINATION_HOST")
    port = os.environ.get("DB_DESTINATION_PORT")
    db = os.environ.get("DB_DESTINATION_NAME")
    username = os.environ.get("DB_DESTINATION_USER")
    password = os.environ.get("DB_DESTINATION_PASSWORD")

    conn = create_engine(
        f"postgresql://{username}:{password}@{host}:{port}/{db}",
        connect_args={"sslmode": sslmode},
    )
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
    sslmode = params.get("sslmode", "require")

    conn = create_connection(sslmode=sslmode)
    data = pd.read_sql(f"select * from {table}", conn)
    conn.dispose()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    data.to_csv(output_path, index=None)


if __name__ == "__main__":
    get_data()
