from typing import Any

from pydantic import BaseModel


class WorkflowCreatedResponse(BaseModel):
    message: str
    dag_id: str
    dag_file: str
    tasks: list[str]
    dependencies: list[list[str]]


class WorkflowRunResponse(BaseModel):
    message: str
    dag_id: str
    run_id: str | None = None
    status: str | None = None


class WorkflowStatusResponse(BaseModel):
    dag_id: str
    run_id: str | None = None
    status: str
    execution_date: str | None = None


class WorkflowOutputResponse(BaseModel):
    message: str
    processed_data: dict[str, Any] | list[Any] | None = None


class HealthResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str
    error_code: str
