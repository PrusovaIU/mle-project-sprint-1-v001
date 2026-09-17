from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

from steps.buildings_flats import create_table, extract, transform, load
from steps.messages import send_telegram_success_message, send_telegram_failure_message


with DAG(
    dag_id='buildings_flats',
    schedule='@once',
    start_date=datetime(2026, 9, 1),
    catchup=False,
    on_success_callback=send_telegram_success_message,
    on_failure_callback=send_telegram_failure_message,
    tags=['buildings', 'flats'],
) as dag:

    create_table_step = PythonOperator(
        task_id='create_table',
        python_callable=create_table,
    )

    extract_step = PythonOperator(
        task_id='extract',
        python_callable=extract,
    )

    transform_step = PythonOperator(
        task_id='transform',
        python_callable=transform,
    )

    load_step = PythonOperator(
        task_id='load',
        python_callable=load,
    )

    create_table_step >> extract_step >> transform_step >> load_step