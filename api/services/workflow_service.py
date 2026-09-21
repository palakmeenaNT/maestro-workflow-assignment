import logging
import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from schemas.request_schema.workflow_request import WorkflowCreateRequest

logger = logging.getLogger(__name__)
GENERATED_DAGS = Path(os.getenv("GENERATED_DAGS_DIR", "/app/dags/generated"))
TEMPLATES = Path(os.getenv("TEMPLATES_DIR", "/app/dags/templates"))


def generate_workflow_dag(workflow: WorkflowCreateRequest) -> Path:
    environment = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=False)
    template = environment.get_template("workflow_dag.py.j2")
    dag_code = template.render(workflow=workflow.model_dump(mode="json"))

    GENERATED_DAGS.mkdir(parents=True, exist_ok=True)
    dag_file = GENERATED_DAGS / f"{workflow.dag_id}.py"
    dag_file.write_text(dag_code, encoding="utf-8")
    logger.info("Generated workflow DAG: dag_id=%s path=%s", workflow.dag_id, dag_file)
    return dag_file
