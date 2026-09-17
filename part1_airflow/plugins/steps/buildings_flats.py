import pandas as pd
from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy import (
    MetaData, Table, Column, Integer, String,
    Float, Boolean
)


def create_table() -> None:
    """
    Создание таблицы, в которую будет записан обработанный датасет
    """
    hook = PostgresHook('destination_db')
    conn = hook.get_sqlalchemy_engine()
    metadata = MetaData()
    Table(
        'buildings_flats',
        metadata,
        Column('building_id', Integer, primary_key=True),
        Column('flat_id', Integer, primary_key=True),
        Column('build_year', Integer),
        Column('building_type_int', Integer),
        Column('latitude', Float),
        Column('longitude', Float),
        Column('ceiling_height', Float),
        Column('flats_count', Integer),
        Column('floors_total', Integer),
        Column('has_elevator', Boolean),
        Column('floor', Integer),
        Column('kitchen_area', Float),
        Column('living_area', Float),
        Column('rooms', Integer),
        Column('is_apartment', Boolean),
        Column('studio', Boolean),
        Column('total_area', Float),
        Column('price', Float),
    )
    metadata.create_all(conn)


def extract(**kwargs) -> None:
    """
    Чтение исходных данных из базы данных. 
    Сохранение данных в XCom.

    :param kwargs: контекст AirFlow.
    """
    ti = kwargs['ti']

    hook = PostgresHook('source_db')
    conn = hook.get_conn()
    sql = """
        select
            b.id as building_id,
            b.build_year,
            b.building_type_int,
            b.latitude,
            b.longitude,
            b.ceiling_height,
            b.flats_count,
            b.floors_total,
            b.has_elevator,
            f.id as flat_id,
            f.floor,
            f.kitchen_area,
            f.living_area,
            f.rooms,
            f.is_apartment,
            f.studio,
            f.total_area,
            f.price
        from buildings as b
        left join flats as f on b.id = f.building_id
    """
    data = pd.read_sql(sql, conn)
    conn.close()

    ti.xcom_push(key='extracted_data', value=data)


def transform(**kwargs) -> None:
    """
    Очистка данных от битых записей и выбросов.
    Обработанные данные сохраняются в XCom.

    :param kwargs: контекст AirFlow.
    """
    ti = kwargs['ti']
    data = ti.xcom_pull(task_ids='extract', key='extracted_data')

    # Удаление объектов, общая площадь которых меньше площади кухни
    filtered_data = data.drop(data[data['kitchen_area'] > data['total_area']].index)

    # Удаление объектов, общая площадь которых меньше суммы жилой площади и площади кухни
    filtered_data = filtered_data.drop(
        filtered_data[
            (filtered_data['kitchen_area'] + filtered_data['living_area']) > filtered_data['total_area']
        ].index
    )

    # Удаление выбросов по площади кухни
    filtered_data = filtered_data.drop(
        filtered_data[(filtered_data['kitchen_area'] < 4) | (filtered_data['kitchen_area'] > 16.5)].index
    )

    # Удаление выбросов по жилой площади
    filtered_data = filtered_data.drop(
        filtered_data[(filtered_data['living_area'] < 8) | (filtered_data['living_area'] > 75)].index
    )

    # Удаление выбросов по общей площади
    filtered_data = filtered_data.drop(
        filtered_data[filtered_data['total_area'] > 121].index
    )

    # Удаление выбросов по высоте потолков
    filtered_data = filtered_data.drop(
        filtered_data[
            (filtered_data['ceiling_height'] < 2.4) | (filtered_data['ceiling_height'] > 3.03)
        ].index
    )

    # Удаление выбросов по стоимости
    filtered_data = filtered_data.drop(
        filtered_data[filtered_data['price'] > 29025000].index
    )

    ti.xcom_push(key='transformed_data', value=filtered_data)


def load(**kwargs):
    """
    Загрузка обработанных данных в целевую таблицу.

    :param kwargs: контекст AirFlow.
    """
    ti = kwargs['ti']
    data = ti.xcom_pull(task_ids='transform', key='transformed_data')

    hook = PostgresHook('destination_db')
    hook.insert_rows(
        table="buildings_flats",
        replace=True,
        target_fields=data.columns.tolist(),
        replace_index=['building_id', 'flat_id'],
        rows=data.values.tolist()
    )
