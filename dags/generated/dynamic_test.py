from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
from airflow.providers.smtp.operators.smtp import EmailOperator


def run_python_task(task_id):
    print(f"Running Python task: {task_id}")


with DAG(
    dag_id="dynamic_test",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["mini-maestro"],
) as dag:




    start_task = PythonOperator(
        task_id="start_task",
        python_callable=run_python_task,
        op_kwargs={
            "task_id": "start_task"
        },
    )





    check_file = FileSensor(
        task_id="check_file",
        filepath="/opt/airflow/input/data.json",
        poke_interval=5,
        timeout=60,
        mode="reschedule",
    )





    notify = EmailOperator(
        task_id="notify",
        to=["palakmeena14@gmail.com"],
        subject="Dynamic workflow test",
        html_content="Dynamic workflow completed.",
    )






    start_task >> check_file

    check_file >> notify
