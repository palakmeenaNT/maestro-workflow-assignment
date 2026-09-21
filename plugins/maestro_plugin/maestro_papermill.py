import json
import logging
from pathlib import Path
from typing import Any

import papermill as pm
from airflow.models import BaseOperator
from airflow.utils.context import Context

logger = logging.getLogger(__name__)


class MaestroPapermillOperator(BaseOperator):

    template_fields = ("input_nb", "output_nb", "result_path", "min_score")

    def __init__(
        self,
        *,
        input_nb: str,
        output_nb: str,
        result_path: str,
        source_task_id: str = "read_data",
        min_score: int | str = 80,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.input_nb = input_nb
        self.output_nb = output_nb
        self.result_path = result_path
        self.source_task_id = source_task_id
        self.min_score = min_score

    def execute(self, context: Context) -> dict[str, Any]:
        raw_data = context["ti"].xcom_pull(task_ids=self.source_task_id, key="raw_data")
        if raw_data is None:
            raise ValueError("No raw_data XCom was found for the Papermill task.")
        Path(self.output_nb).parent.mkdir(parents=True, exist_ok=True)
        Path(self.result_path).parent.mkdir(parents=True, exist_ok=True)
        pm.execute_notebook(
            self.input_nb,
            self.output_nb,
            parameters={"raw_data": raw_data, "min_score": int(self.min_score), "result_path": self.result_path},
            log_output=True,
        )
        with open(self.result_path, encoding="utf-8") as result_file:
            processed_data = json.load(result_file)
        context["ti"].xcom_push(key="processed_data", value=processed_data)
        logger.info("Papermill created processed_data: total_qualified=%s", processed_data.get("total_qualified"))
        return processed_data
