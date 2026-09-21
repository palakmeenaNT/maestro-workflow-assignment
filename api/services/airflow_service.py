import logging
import os
from typing import Any

import requests

from schemas.response_schema.workflow_response import WorkflowRunResponse, WorkflowStatusResponse

logger = logging.getLogger(__name__)
AIRFLOW_URL = os.getenv("AIRFLOW_URL", "http://localhost:8082")
AIRFLOW_USERNAME = os.getenv("AIRFLOW_USERNAME", "admin")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD", "admin")


def trigger_workflow(dag_id: str, conf: dict[str, Any]) -> WorkflowRunResponse:
    response = _request_airflow("POST", f"/api/v1/dags/{dag_id}/dagRuns", json={"conf": conf})
    payload = response.json()
    logger.info("Triggered Airflow workflow: dag_id=%s run_id=%s", dag_id, payload.get("dag_run_id"))
    return WorkflowRunResponse(
        message="Workflow triggered successfully.",
        dag_id=dag_id,
        run_id=payload.get("dag_run_id"),
        status=payload.get("state"),
    )


def get_workflow_status(dag_id: str) -> WorkflowStatusResponse:
    response = _request_airflow(
        "GET", f"/api/v1/dags/{dag_id}/dagRuns", params={"order_by": "-execution_date", "limit": 1}
    )
    dag_runs = response.json().get("dag_runs", [])
    if not dag_runs:
        return WorkflowStatusResponse(dag_id=dag_id, status="not_started")
    latest_run = dag_runs[0]
    return WorkflowStatusResponse(
        dag_id=dag_id,
        run_id=latest_run.get("dag_run_id"),
        status=latest_run.get("state", "unknown"),
        execution_date=latest_run.get("execution_date"),
    )


def _request_airflow(method: str, path: str, **kwargs: Any) -> requests.Response:
    response = requests.request(
        method,
        f"{AIRFLOW_URL}{path}",
        auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD),
        timeout=10,
        **kwargs,
    )
    response.raise_for_status()
    return response
