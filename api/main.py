from fastapi import FastAPI

from core.logging import configure_logging
from exceptions.workflow_exceptions import WorkflowException
from handlers.exception_handlers import workflow_exception_handler
from routes.workflow_routes import router
from schemas.response_schema.workflow_response import HealthResponse

configure_logging()
app = FastAPI(
    title="Mini-Maestro API",
    
)
app.add_exception_handler(WorkflowException, workflow_exception_handler)
app.include_router(router)


@app.get("/", response_model=HealthResponse)
def home() -> HealthResponse:
    return HealthResponse(message="Mini-Maestro API is running")
