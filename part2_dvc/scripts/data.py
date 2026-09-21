
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
import os
from dotenv import load_dotenv
import yaml



def create_connection() -> Engine:
    """
    Создание подключения к БД с датасетом.
    Параметры подключения запрашиваются из файла .env:

    - DB_DESTINATION_HOST
    - DB_DESTINATION_PORT
    - DB_DESTINATION_NAME
    - DB_DESTINATION_USER
    - DB_DESTINATION_PASSWORD

    :return: новое подключение к БД.
    """
    load_dotenv()
    host = os.environ.get('DB_DESTINATION_HOST')
    port = os.environ.get('DB_DESTINATION_PORT')
    db = os.environ.get('DB_DESTINATION_NAME')
    username = os.environ.get('DB_DESTINATION_USER')
    password = os.environ.get('DB_DESTINATION_PASSWORD')
    
    print(f'postgresql://{username}:{password}@{host}:{port}/{db}')
    conn = create_engine(f'postgresql://{username}:{password}@{host}:{port}/{db}', connect_args={'sslmode':'require'})
    return conn


def get_data():
    """
    Загрузка данных: данные выгпружаются из БД и сохраняются в файл data/initial.csv

    В проуессе выполнения задачи загружаются гиперпараметры:
    - table
    """
    # загрузка гиперпараметров
    with open('params.yaml', 'r') as fd:
        params = yaml.safe_load(fd)

    conn = create_connection()
    data = pd.read_sql(f'select * from {params['table']}', conn)
    conn.dispose()

    os.makedirs('data', exist_ok=True)
    data.to_csv('data/initial_data.csv', index=None)


if __name__ == '__main__':
    get_data()
