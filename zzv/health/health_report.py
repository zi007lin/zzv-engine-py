from typing import List

from health.status import Status  # Import the Status enumeration


class HealthReport:
    """
    Class representing the health status of a service or manager.
    """

    def __init__(self, manager_name: str, status, details: List[str] = None):
        """
        Initialize the HealthReport object.

        Args:
            manager_name (str): The name of the manager or service.
            status (Status or str): The health status, either as a Status enum or a string.
            details (List[str], optional): Additional health details. Defaults to an empty list.
        """
        self.manager_name = manager_name

        # Ensure that the status is of type Status, not a string
        if isinstance(status, str):
            try:
                self.status = Status[status]  # Convert string to Status enum
            except KeyError:
                raise ValueError(f"Invalid status string '{status}'. Must be one of {list(Status.__members__.keys())}.")
        elif isinstance(status, Status):
            self.status = status
        else:
            raise TypeError(f"status must be of type 'Status' or 'str', but got {type(status)}.")

        self.details = details if details is not None else []

    def to_dict(self):
        """
        Convert the HealthReport object to a dictionary format.

        Returns:
            dict: Dictionary representation of the health report.
        """
        return {
            'manager_name': self.manager_name,
            'status': self.status.value,  # Convert enum to its value for serialization
            'details': self.details
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
