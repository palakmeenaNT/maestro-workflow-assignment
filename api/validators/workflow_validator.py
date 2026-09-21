import ast
import re

from email_validator import EmailNotValidError, validate_email

from exceptions.workflow_exceptions import WorkflowException
from enums.operator_enum import OperatorType
from schemas.request_schema.workflow_request import TaskRequest, WorkflowCreateRequest


def validate_workflow_definition(workflow: WorkflowCreateRequest) -> None:
    validate_dag_id(workflow.dag_id)
    task_ids = validate_tasks(workflow.tasks)
    validate_dependencies(workflow.dependencies, task_ids)


def validate_dag_id(dag_id: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", dag_id):
        raise WorkflowException(
            "Invalid dag_id. Only letters, numbers, '.', '-' and '_' are allowed.",
            error_code="invalid_dag_id",
        )


def validate_tasks(tasks: list[TaskRequest]) -> set[str]:
    task_ids: set[str] = set()
    function_names: set[str] = set()
    for task in tasks:
        task_id = task.task_id.strip()
        if not task_id:
            raise WorkflowException("task_id cannot be empty.", error_code="invalid_task")
        if task_id in task_ids:
            raise WorkflowException(f"Duplicate task_id: '{task_id}'", error_code="duplicate_task")
        if task.operator == OperatorType.PYTHON:
            _validate_python_function(task, function_names)
        elif task.function is not None:
            raise WorkflowException(
                f"Only Python task '{task.task_id}' may define a function.",
                error_code="invalid_function",
            )
        _validate_task_config(task)
        task_ids.add(task_id)
    return task_ids


def _validate_python_function(task: TaskRequest, function_names: set[str]) -> None:
    if task.function is None:
        raise WorkflowException(
            f"Python task '{task.task_id}' requires a function with name and source.",
            error_code="missing_function",
        )
    if task.function.name in function_names:
        raise WorkflowException(
            f"Duplicate Python function name: '{task.function.name}'.",
            error_code="duplicate_function",
        )
    try:
        parsed_source = ast.parse(task.function.source)
    except SyntaxError as error:
        raise WorkflowException(
            f"Function source for task '{task.task_id}' is not valid Python: {error.msg}",
            error_code="invalid_function",
        ) from error
    if not any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == task.function.name
        for node in parsed_source.body
    ):
        raise WorkflowException(
            f"Function source for task '{task.task_id}' must define '{task.function.name}'.",
            error_code="invalid_function",
        )
    function_names.add(task.function.name)


def _validate_task_config(task: TaskRequest) -> None:
    if task.operator == OperatorType.FILE_SENSOR:
        filepath = task.config.get("filepath")
        if not isinstance(filepath, str) or not filepath.strip():
            raise WorkflowException(
                "FileSensor 'filepath' is required and must be a non-empty string.",
                error_code="invalid_file_sensor_config",
            )
    if task.operator == OperatorType.EMAIL:
        recipients = task.config.get("to")
        if not isinstance(recipients, list) or not recipients:
            raise WorkflowException(
                "EmailOperator 'to' is required and must be a non-empty list.",
                error_code="invalid_email_config",
            )
        for email in recipients:
            if not isinstance(email, str):
                raise WorkflowException(
                    "Each EmailOperator recipient must be a string.",
                    error_code="invalid_email_config",
                )
            try:
                validate_email(email, check_deliverability=False)
            except EmailNotValidError as error:
                raise WorkflowException(
                    f"Invalid email address: '{email}'",
                    error_code="invalid_email_config",
                ) from error


def validate_dependencies(dependencies: list[list[str]], task_ids: set[str]) -> None:
    dependency_set: set[tuple[str, str]] = set()
    graph = {task_id: [] for task_id in task_ids}
    for dependency in dependencies:
        if len(dependency) != 2:
            raise WorkflowException(
                "Each dependency must contain exactly [upstream_task, downstream_task].",
                error_code="invalid_dependency",
            )
        upstream, downstream = dependency
        if not all(isinstance(task_id, str) and task_id.strip() for task_id in dependency):
            raise WorkflowException(f"Invalid dependency: {dependency}", error_code="invalid_dependency")
        if upstream not in task_ids or downstream not in task_ids or upstream == downstream:
            raise WorkflowException(f"Invalid dependency: {dependency}", error_code="invalid_dependency")
        edge = (upstream, downstream)
        if edge in dependency_set:
            raise WorkflowException(
                f"Duplicate dependency: '{upstream}' -> '{downstream}'",
                error_code="duplicate_dependency",
            )
        dependency_set.add(edge)
        graph[upstream].append(downstream)
    _validate_no_cycles(graph)


def _validate_no_cycles(graph: dict[str, list[str]]) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str) -> None:
        if task_id in visiting:
            raise WorkflowException("Circular dependency detected in workflow.", error_code="circular_dependency")
        if task_id in visited:
            return
        visiting.add(task_id)
        for downstream in graph[task_id]:
            visit(downstream)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in graph:
        visit(task_id)
