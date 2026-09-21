import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from exceptions.workflow_exceptions import WorkflowException
from schemas.response_schema.workflow_response import ErrorResponse

logger = logging.getLogger(__name__)


def workflow_exception_handler(request: Request, exception: WorkflowException) -> JSONResponse:
    logger.warning(
        "Workflow request failed: path=%s code=%s message=%s",
        request.url.path,
        exception.error_code,
        exception.message,
    )
    response = ErrorResponse(detail=exception.message, error_code=exception.error_code)
    return JSONResponse(status_code=400, content=response.model_dump())
