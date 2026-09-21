from typing import Any

from pydantic import BaseModel, Field

from enums.operator_enum import OperatorType


class PythonFunctionRequest(BaseModel):

    name: str = Field(min_length=1, pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")
    source: str = Field(min_length=1)


class TaskRequest(BaseModel):
    task_id: str = Field(min_length=1)
    operator: OperatorType
    config: dict[str, Any] = Field(default_factory=dict)
    function: PythonFunctionRequest | None = None


class WorkflowCreateRequest(BaseModel):
    dag_id: str = Field(min_length=1)
    tasks: list[TaskRequest] = Field(min_length=1)
    dependencies: list[list[str]] = Field(default_factory=list)


class WorkflowRunRequest(BaseModel):

    dag_id: str = "sample_data_workflow"
    conf: dict[str, Any] = Field(default_factory=dict)
