from enum import Enum


class Status(Enum):
    """Enumeration for health status types."""
    OK = "OK"
    ERROR = "ERROR"
    WARNING = "WARNING"
    UNKNOWN = "UNKNOWN"
