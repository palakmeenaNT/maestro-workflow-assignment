import json
import logging
from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.standard.sensors.filesystem import FileSensor
from maestro_plugin.maestro_papermill import MaestroPapermillOperator

logger = logging.getLogger(__name__)
INPUT_FILE = "/opt/airflow/input/data.json"
OUTPUT_FILE = "/opt/airflow/output/result.json"


def read_data(file_path: str, **context) -> None:
    """Read the input file and publish it with the required XCom key."""
    with open(file_path, encoding="utf-8") as file:
        data = json.load(file)
    context["ti"].xcom_push(key="raw_data", value=data)
    logger.info("Read %s records from %s", len(data), file_path)


def save_result(output_path: str, **context) -> None:
    """Persist the Papermill result published with the required XCom key."""
    processed_data = context["ti"].xcom_pull(task_ids="process_data", key="processed_data")
    if processed_data is None:
        raise ValueError("No processed_data XCom was found.")
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(processed_data, indent=2), encoding="utf-8")
    logger.info("Saved processed result to %s", output_file)


with DAG(
    dag_id="sample_data_workflow",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["mini-maestro", "papermill"],
) as dag:
    file_sensor = FileSensor(
        task_id="file_sensor", filepath=INPUT_FILE, poke_interval=10, timeout=300, mode="reschedule"
    )
    read_data_task = PythonOperator(
        task_id="read_data", python_callable=read_data, op_kwargs={"file_path": INPUT_FILE}
    )
    process_data_task = MaestroPapermillOperator(
        task_id="process_data",
        input_nb="/opt/airflow/notebooks/process_data.ipynb",
        output_nb="/opt/airflow/output/executed_process_data.ipynb",
        result_path="/opt/airflow/output/papermill_result.json",
        min_score=80,
    )
    save_result_task = PythonOperator(
        task_id="save_result", python_callable=save_result, op_kwargs={"output_path": OUTPUT_FILE}
    )

    file_sensor >> read_data_task >> process_data_task >> save_result_task
