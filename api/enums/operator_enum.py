from enum import Enum


class OperatorType(str, Enum):
    PYTHON = "python"
    FILE_SENSOR = "file_sensor"
    EMAIL = "email"