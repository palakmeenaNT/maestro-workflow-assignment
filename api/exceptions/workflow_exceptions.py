class WorkflowException(Exception):

    def __init__(
        self,
        message: str,
        *,
        error_code: str = "workflow_error",
    ) -> None:
        self.message = message
        self.error_code = error_code
        super().__init__(message)
