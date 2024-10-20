from typing import List

from health.status import Status  # Import the Status enumeration


from enum import Enum

class Status(Enum):
    OK = "OK"
    ERROR = "ERROR"

class HealthReport:
    """
    Class representing the health status of a service or manager.
    """

    def __init__(self, manager_name: str, status: Status, details: list):
        self.manager_name = manager_name
        self.status = status.value if isinstance(status, Status) else status
        self.details = details

    def to_dict(self):
        return {
            "manager_name": self.manager_name,
            "status": self.status,
            "details": self.details
        }

    def combine(self, other_report):
        """
        Combine this health report with another health report.

        Args:
            other_report (HealthReport): Another health report to combine with.

        Raises:
            ValueError: If the health status of the other report is not OK.
        """
        # Ensure the other_report's status is of type Status
        if isinstance(other_report.status, str):
            other_report.status = Status[other_report.status]

        if other_report.status != Status.OK:
            self.status = Status.ERROR  # Update status to ERROR if any combined report has an issue
        self.details.extend(other_report.details)  # Merge the details lists
