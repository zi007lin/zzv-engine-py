import asyncio
import logging
import sys
from typing import Optional, List, Dict

from fastapi import FastAPI

from engine.kernel_aware_manager import KernelAwareManager
from zzv.common.constants import QUEUE_MANAGER, MSG_MANAGER
from zzv.engine.manager import Manager
from zzv.health.health_report import HealthReport
from zzv.health.status import Status
from zzv.msgcore.msg_manager import MsgManager
from zzv.msgcore.queue_manager import QueueManager

logger = logging.getLogger(__name__)


class Kernel(Manager):
    def __init__(self, config, additional_managers: Optional[List[Dict]] = None):
        """
        Initialize the Kernel with configuration and additional managers.

        Args:
            config (dict): Configuration dictionary.
            additional_managers (list, optional): List of additional manager configurations.
        """
        self._services = {}
        self.is_running = False  # Track running status
        self._service_access_rules = {}  # Dictionary to hold access rules for services
        self.config = config  # Store the configuration for use in services
        self._additional_managers = additional_managers or []  # List of additional managers

        # Load Kafka broker information from config
        kafka_brokers = self.config.get('kafka_brokers',
                                        '31.220.102.46:29092,31.220.102.46:29094')  # Default to localhost if not set

        # Register core services
        self._register_service(QUEUE_MANAGER, QueueManager(self, kafka_brokers), allowed_callers=["*"])
        self._register_service(MSG_MANAGER, MsgManager(self), allowed_callers=["*"])

        # Register additional managers provided in the configuration
        self._register_additional_managers()

    def _register_additional_managers(self):
        """
        Register additional managers based on the provided configuration.
        """
        for manager_config in self._additional_managers:
            name = manager_config.get("name")
            instance = manager_config.get("instance")
            allowed_callers = manager_config.get("allowed_callers", ["*"])

            if name and instance:
                # Set the kernel reference if the manager implements KernelAwareManager
                if isinstance(instance, KernelAwareManager):
                    instance.set_kernel(self)
                    logger.info(f"Kernel reference set for manager '{name}'.")

                self._register_service(name, instance, allowed_callers=allowed_callers)
                logger.info(f"Additional manager '{name}' registered successfully.")
            else:
                logger.error(f"Failed to register additional manager. Invalid configuration: {manager_config}")

    def _register_service(self, name: str, service: Manager, allowed_callers=None):
        """
        Register a service with the kernel with optional access control.
        """
        try:
            self._services[name] = service
            self._service_access_rules[name] = allowed_callers or []
        except Exception as e:
            logger.error(f"Error registering service {name}: {e}")
            sys.exit(2)  # Exit with error code 2 for service registration errors

    def get_service(self, service_name: str, **kwargs) -> Optional[Manager]:
        """
        Retrieve a registered service by name with optional caller validation.
        """
        caller = kwargs.get('caller', None)  # Extract caller from kwargs if provided
        caller_name = caller.__class__.__name__ if caller else "Unknown Caller"

        if service_name not in self._services:
            logger.error(f"Service '{service_name}' is not registered.")
            sys.exit(3)  # Exit with error code 3 for service not found errors

        # Validate caller's access rights
        allowed_callers = self._service_access_rules.get(service_name, [])
        if "*" in allowed_callers or caller_name in allowed_callers:
            return self._services[service_name]
        else:
            logger.error(f"Access denied: '{caller_name}' is not allowed to access '{service_name}'.")
            sys.exit(4)  # Exit with error code 4 for access denied errors

    async def start(self):
        """
        Start all registered services asynchronously.
        """
        if self.is_running:
            logger.error("Kernel is already running. Cannot start services again.")
            return  # Return early if the Kernel is already running

        logger.info("Starting all registered services asynchronously...")
        self.is_running = True  # Set running status to True when starting

        # Start core services
        for name, service in self._services.items():
            if isinstance(service, Manager):
                try:
                    # Start each service asynchronously without waiting
                    asyncio.create_task(service.start())
                    logger.info(f"{name} started asynchronously.")
                except Exception as e:
                    logger.error(f"Failed to start service {name}: {e}")
                    sys.exit(5)  # Exit with error code 5 for service start errors

        # Start additional managers
        for manager in self._additional_managers:
            instance = manager.get("instance")
            if instance and isinstance(instance, KernelAwareManager):
                try:
                    await instance.start()  # Await each additional manager's start
                    logger.info(f"Additional manager '{manager['name']}' started successfully.")
                except Exception as e:
                    logger.error(f"Failed to start additional manager '{manager['name']}': {e}")
                    sys.exit(5)

    async def close(self):
        """
        Stop all registered services asynchronously.
        """
        logger.info("Stopping all registered services asynchronously...")
        self.is_running = False  # Set running status to False when stopping

        # Stop core services
        for name, service in self._services.items():
            if isinstance(service, Manager):
                try:
                    await service.close()
                    logger.info(f"{name} stopped successfully.")
                except Exception as e:
                    logger.error(f"Failed to stop service {name}: {e}")
                    sys.exit(6)  # Exit with error code 6 for service stop errors

        # Stop additional managers
        for manager in self._additional_managers:
            instance = manager.get("instance")
            if instance and isinstance(instance, KernelAwareManager):
                try:
                    await instance.close()  # Await each additional manager's close
                    logger.info(f"Additional manager '{manager['name']}' stopped successfully.")
                except Exception as e:
                    logger.error(f"Failed to stop additional manager '{manager['name']}': {e}")
                    sys.exit(6)

    def get_health(self) -> HealthReport:
        """
        Retrieve the combined health status of all registered managers.
        """
        try:
            health_report = HealthReport(manager_name="Kernel", status=Status.OK, details=[])
            for manager_name, manager_instance in self._services.items():
                service_health = manager_instance.get_health()
                health_report.combine(service_health)
            return health_report
        except Exception as e:
            logger.error(f"Failed to retrieve combined health report: {e}")
            return HealthReport(
                manager_name="Kernel",
                status=Status.ERROR,  # Use Status.ERROR to indicate failure
                details=[f"Error: {str(e)}"]
            )

    def register_endpoints(self, app: FastAPI):
        """
        Register custom endpoints for the Kernel and all managed managers.

        Args:
            app (FastAPI): The main FastAPI application where endpoints should be registered.
        """
        # Call the register_endpoints method of each managed manager to add their endpoints
        for manager in self._services.values():  # Use .values() to get the manager instances, not keys
            if hasattr(manager, 'register_endpoints'):
                manager.register_endpoints(app)
                logger.info(f"Registered endpoints for manager: {manager.name}.")
            else:
                logger.warning(f"Manager {manager} does not have a register_endpoints method.")

        logger.info(f"Registered endpoints for Kernel and all managed managers.")

