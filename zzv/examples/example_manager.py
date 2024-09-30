import logging

from zzv.health.health_report import HealthReport
from zzv.engine.manager import Manager  # Ensure correct import of the Manager class

logger = logging.getLogger(__name__)

class ExampleManager(Manager):
    def __init__(self):
        super(ExampleManager, self).__init__(name="ExampleManager")
        self._running = False
        self._services = {}

    async def start(self):
        """
        Start the ExampleManager.
        """
        if not self._running:
            self._running = True
            logger.info(f"{self.name} started.")

    async def close(self):
        """
        Stop the ExampleManager.
        """
        if self._running:
            self._running = False
            logger.info(f"{self.name} stopped.")

    def get_health(self):
        """
        Return the health status of the ExampleManager as a HealthReport object.
        """
        status = "OK" if self._running else "ERROR"
        # Create a HealthReport object with the manager name, status, and additional details
        return HealthReport(
            manager_name=self.name,
            status=status,
            details=["ExampleManager health check successful" if self._running else "ExampleManager is not running."]
        )

    def register_endpoints(self, app):
        """
        Register custom endpoints for the ExampleManager.

        Args:
            app (FastAPI): The main FastAPI app where endpoints should be registered.
        """

        @app.get(f"/{self.name}/health")
        async def example_manager_health():
            """
            Endpoint to get the health status of the ExampleManager.
            """
            return {"manager": self.name, "health_status": self.get_health().to_dict()}

    def _register_service(self, name, service):
        """
        Register a service for the manager.

        Args:
            name (str): The name of the service to register.
            service (object): The service instance to be registered.
        """
        self._services[name] = service
        logger.info(f"Service '{name}' registered successfully.")

    def get_service(self, name):
        """
        Retrieve a service by name.

        Args:
            name (str): The name of the service to retrieve.

        Returns:
            object: The service instance if found, or None if not found.
        """
        return self._services.get(name, None)