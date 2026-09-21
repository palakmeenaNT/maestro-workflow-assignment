import json
import logging
import os
from pathlib import Path

from fastapi import APIRouter, Depends

from schemas.request_schema.workflow_request import WorkflowCreateRequest, WorkflowRunRequest
from schemas.response_schema.workflow_response import (
    WorkflowCreatedResponse,
    WorkflowOutputResponse,
    WorkflowRunResponse,
    WorkflowStatusResponse,
)
from services.airflow_service import get_workflow_status, trigger_workflow
from services.workflow_service import generate_workflow_dag
from validators.workflow_validator import validate_workflow_definition

logger = logging.getLogger(__name__)
router = APIRouter()
OUTPUT_FILE = Path(os.getenv("OUTPUT_FILE", "/app/output/result.json"))


def validated_workflow(workflow: WorkflowCreateRequest) -> WorkflowCreateRequest:
    validate_workflow_definition(workflow)
    return workflow


@router.post("/workflows", response_model=WorkflowCreatedResponse, status_code=201)
def create_workflow(workflow: WorkflowCreateRequest = Depends(validated_workflow)) -> WorkflowCreatedResponse:
    dag_file = generate_workflow_dag(workflow)
    logger.info("workflow definition accepted: dag_id=%s", workflow.dag_id)
    return WorkflowCreatedResponse(
        message="Workflow created successfully.",
        dag_id=workflow.dag_id,
        dag_file=str(dag_file),
        tasks=[task.task_id for task in workflow.tasks],
        dependencies=workflow.dependencies,
    )


@router.post("/run-workflow", response_model=WorkflowRunResponse)
def run_workflow(request: WorkflowRunRequest | None = None) -> WorkflowRunResponse:
    request = request or WorkflowRunRequest()
    return trigger_workflow(request.dag_id, request.conf)


@router.get("/status", response_model=WorkflowStatusResponse)
def workflow_status(dag_id: str = "sample_data_workflow") -> WorkflowStatusResponse:
    return get_workflow_status(dag_id)


@router.get("/show-output", response_model=WorkflowOutputResponse)
def show_output() -> WorkflowOutputResponse:
    if not OUTPUT_FILE.exists():
        return WorkflowOutputResponse(message="Output file does not exist yet.")
    processed_data = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
    return WorkflowOutputResponse(message="Workflow output retrieved successfully.", processed_data=processed_data)
