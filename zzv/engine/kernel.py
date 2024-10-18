import asyncio
import logging
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
    def __init__(self, config, additional_managers: Optional[List[Dict]] = None, name: str = "Kernel"):
        super().__init__(name=name)  # Initialize the parent Manager class with the name
        self._services = {}
        self.is_running = False
        self._service_access_rules = {}
        self.config = config
        self._additional_managers = additional_managers or []

        kafka_brokers = self.config.get('kafka_brokers', '31.220.102.46:29092,31.220.102.46:29094')

        self._register_service(QUEUE_MANAGER, QueueManager(self, kafka_brokers), allowed_callers=["*"])
        self._register_service(MSG_MANAGER, MsgManager(self), allowed_callers=["*"])

        self._register_additional_managers()

    def _register_additional_managers(self):
        for manager_config in self._additional_managers:
            name = manager_config.get("name")
            instance = manager_config.get("instance")
            allowed_callers = manager_config.get("allowed_callers", ["*"])

            if name and instance:
                if isinstance(instance, KernelAwareManager):
                    instance.set_kernel(self)
                    logger.info(f"Kernel reference set for manager '{name}'.")

                self._register_service(name, instance, allowed_callers=allowed_callers)
                logger.info(f"Additional manager '{name}' registered successfully.")
            else:
                logger.error(f"Failed to register additional manager. Invalid configuration: {manager_config}")

    def _register_service(self, name: str, service: Manager, allowed_callers=None):
        try:
            self._services[name] = service
            self._service_access_rules[name] = allowed_callers or []
            logger.info(f"Service '{name}' registered successfully.")
        except Exception as e:
            logger.error(f"Error registering service {name}: {e}")
            raise  # Raise the exception instead of exiting

    def get_service(self, service_name: str, **kwargs) -> Optional[Manager]:
        caller = kwargs.get('caller', None)
        caller_name = caller.__class__.__name__ if caller else "Unknown Caller"

        if service_name not in self._services:
            logger.error(f"Service '{service_name}' is not registered.")
            return None

        allowed_callers = self._service_access_rules.get(service_name, [])
        if "*" in allowed_callers or caller_name in allowed_callers:
            return self._services[service_name]
        else:
            logger.error(f"Access denied: '{caller_name}' is not allowed to access '{service_name}'.")
            return None

    async def start(self):
        if self.is_running:
            logger.warning("Kernel is already running. Skipping start process.")
            return

        logger.info("Starting all registered services asynchronously...")
        self.is_running = True

        start_tasks = []
        for name, service in self._services.items():
            if isinstance(service, Manager):
                start_tasks.append(self._start_service(name, service))

        for manager in self._additional_managers:
            instance = manager.get("instance")
            if isinstance(instance, KernelAwareManager):
                start_tasks.append(self._start_manager(manager['name'], instance))

        await asyncio.gather(*start_tasks)

    async def _start_service(self, name, service):
        try:
            await service.start()
            logger.info(f"{name} started successfully.")
        except Exception as e:
            logger.error(f"Failed to start service {name}: {e}")
            self.is_running = False
            raise

    async def _start_manager(self, name, instance):
        try:
            await instance.start()
            logger.info(f"Additional manager '{name}' started successfully.")
        except Exception as e:
            logger.error(f"Failed to start additional manager '{name}': {e}")
            self.is_running = False
            raise

    async def close(self):
        if not self.is_running:
            logger.warning("Kernel is not running. Skipping close process.")
            return

        logger.info("Stopping all registered services asynchronously...")
        self.is_running = False

        close_tasks = []
        for name, service in self._services.items():
            if isinstance(service, Manager):
                close_tasks.append(self._close_service(name, service))

        for manager in self._additional_managers:
            instance = manager.get("instance")
            if isinstance(instance, KernelAwareManager):
                close_tasks.append(self._close_manager(manager['name'], instance))

        await asyncio.gather(*close_tasks)

    async def _close_service(self, name, service):
        try:
            await service.close()
            logger.info(f"{name} stopped successfully.")
        except Exception as e:
            logger.error(f"Failed to stop service {name}: {e}")

    async def _close_manager(self, name, instance):
        try:
            await instance.close()
            logger.info(f"Additional manager '{name}' stopped successfully.")
        except Exception as e:
            logger.error(f"Failed to stop additional manager '{name}': {e}")

    def get_health(self):
        logger.debug("Kernel: Entering get_health method")
        manager_health_reports = []
        overall_status = Status.OK if self.is_running else Status.ERROR

        for name, service in self._services.items():
            health_report = self._get_manager_health(name, service)
            manager_health_reports.append(health_report)
            if health_report.status == Status.ERROR:
                overall_status = Status.ERROR

        for manager in self._additional_managers:
            health_report = self._get_manager_health(manager.get('name'), manager.get('instance'))
            manager_health_reports.append(health_report)
            if health_report.status == Status.ERROR:
                overall_status = Status.ERROR

        final_report = HealthReport(
            manager_name="Kernel",
            status=overall_status,
            details=[report.to_dict() for report in manager_health_reports]
        )
        logger.debug(f"Kernel: Final health report: {final_report.to_dict()}")
        return final_report

    def _get_manager_health(self, name, instance):
        try:
            if hasattr(instance, 'get_health'):
                health_report = instance.get_health()
                if health_report is None:
                    raise ValueError("Health check returned None")
                return health_report
            else:
                return HealthReport(
                    manager_name=name,
                    status=Status.WARNING,
                    details=[f"No health check method available for {name}"]
                )
        except Exception as e:
            logger.error(f"Error getting health for {name}: {e}")
            return HealthReport(
                manager_name=name,
                status=Status.ERROR,
                details=[f"Error in health check: {str(e)}"]
            )

    def register_endpoints(self, app: FastAPI):
        for manager in self._services.values():
            if hasattr(manager, 'register_endpoints'):
                manager.register_endpoints(app)
                logger.info(f"Registered endpoints for manager: {manager.name}.")
            else:
                logger.debug(f"Manager {manager} does not have a register_endpoints method.")

        @app.get("/health")
        async def health_check():
            return self.get_health().to_dict()

        logger.info("Registered endpoints for Kernel and all managed managers.")