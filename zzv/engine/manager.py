from abc import ABC, abstractmethod
from zzv.health.health_report import HealthReport
from zzv.health.status import Status  # Import the Status enumeration
from zzv.health.health import Health  # Import the Health base class

class Manager(Health, ABC):
    """
    Abstract base class for all managers. Provides a method for registering custom endpoints and managing services.
    Inherits from Health to implement health-check functionalities and ABC for abstract methods.
    """

    def __init__(self, name: str):
        """
        Initialize the base Manager class with a name and default health status.

        Args:
            name (str): The name of the manager, used for endpoint grouping and logging.
        """
        super().__init__()  # Call the Health base class initializer
        self.name = name  # Store the name of the manager
        self._running = False  # Attribute to track if the manager is currently running
        self._services = {}  # Initialize a dictionary to hold registered services

    @abstractmethod
    def start(self):
        """
        Abstract method to start the manager. Should be implemented by derived classes.
        """
        pass

    @abstractmethod
    def close(self):
        """
        Abstract method to stop/close the manager. Should be implemented by derived classes.
        """
        pass

    def get_status(self) -> Status:
        """
        Retrieve the current status of the manager.

        Returns:
            Status: The current health status of the manager as an enumeration.
        """
        return Status.OK if self._running else Status.ERROR  # Return Status.OK if running, otherwise Status.ERROR

    def get_health(self) -> HealthReport:
        """
        Retrieve the health status of the manager as a HealthReport object.

        Returns:
            HealthReport: A HealthReport object indicating the health status of the manager.
        """
        status = self.get_status()  # Use the get_status method to determine the health status
        return HealthReport(
            manager_name=self.name,
            status=status,  # Pass the Status enumeration instead of a string
            details=[f"{self.name} is running" if self._running else f"{self.name} is not running."]
        )
