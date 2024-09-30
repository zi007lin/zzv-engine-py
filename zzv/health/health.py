from abc import ABC, abstractmethod

class Health(ABC):
    """
    Abstract base class for health-related functionality.
    This class should define the health-check interface for other classes to implement.
    """

    @abstractmethod
    def get_health(self):
        """
        Abstract method to retrieve the health status.
        This method should be implemented by any class that inherits Health.

        Returns:
            HealthReport: The health report object for the service/manager.
        """
        pass
