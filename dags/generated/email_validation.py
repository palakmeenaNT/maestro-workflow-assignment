from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
from airflow.providers.smtp.operators.smtp import EmailOperator


def run_python_task(task_id):
    print(f"Running Python task: {task_id}")


with DAG(
    dag_id="email_validation",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["mini-maestro"],
) as dag:




    send_email = EmailOperator(
        task_id="send_email",
        to=["hello"],
        subject="Workflow completed",
        html_content="The Workflow has completed successfully.",
    )





