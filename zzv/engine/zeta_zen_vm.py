import asyncio
import logging
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from zzv.common.constants import KERNEL
from zzv.common.utility import load_config, start_server_request, check_health
from zzv.engine.kernel import Kernel

logger = logging.getLogger(__name__)

# Define the default path to the configuration file
DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')


class ZetaZenVm:
    def __init__(self, config=None, config_path=DEFAULT_CONFIG_PATH, additional_managers=None):
        """
        Initialize the ZetaZenVm with a configuration and additional managers.

        Args:
            config (dict, optional): Configuration dictionary. Defaults to None.
            config_path (str, optional): Path to the configuration file. Defaults to 'config/config.yaml'.
            additional_managers (list, optional): List of additional manager configurations. Defaults to None.
        """
        config_path = os.path.abspath(config_path)
        if config is None:
            config = load_config(config_path)

        self.config = config
        self.additional_managers = additional_managers or []  # Set default to empty list if not provided

        # Initialize the Kernel instance
        self.kernel = Kernel(self.config, additional_managers=self.additional_managers)

        # Initialize FastAPI app with metadata and set up endpoints
        self.app = FastAPI(
            title="Zeta Zen Vm",
            description="Zeta Zen Vm is a server-side base implementation designed to serve as the foundation for various projects within the zzv ecosystem.",
            version="1.0.0",
            terms_of_service="http://zzv.io/terms/",
            contact={
                "name": "Support Team",
                "url": "http://zzv.io/contact",
                "email": "support@zzv.io",
            },
            license_info={
                "name": "Apache 2.0",
                "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
            }
        )

        # Register endpoints for the kernel and all its managers
        self.kernel.register_endpoints(self.app)  # Invoke register_endpoints on kernel

        # Set up additional REST API endpoints for controlling the server
        self._setup_endpoints()

    def _setup_endpoints(self):
        """Define custom REST API endpoints controlling the server and its services."""
        @self.app.post('/start')
        async def start_all():
            try:
                await self.kernel.start()  # Awaiting the coroutine
                return {"status": "All services started successfully"}
            except Exception as e:
                logger.error(f"Failed to start all services: {e}")
                raise HTTPException(status_code=500, detail="Failed to start all services")

        @self.app.post('/stop')
        async def stop_all():
            try:
                await self.kernel.close()  # Awaiting the coroutine
                return {"status": "All services stopped successfully"}
            except Exception as e:
                logger.error(f"Failed to stop all services: {e}")
                raise HTTPException(status_code=500, detail="Failed to stop all services")

        @self.app.post('/start/{service_name}')
        async def start_service(service_name: str):
            try:
                service = self.kernel.get_service(service_name)
                if service:
                    await service.start()  # Awaiting the coroutine
                    return {"status": f"Service {service_name} started successfully"}
                else:
                    raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
            except Exception as e:
                logger.error(f"Failed to start service {service_name}: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to start service {service_name}")

        @self.app.post('/stop/{service_name}')
        async def stop_service(service_name: str):
            try:
                service = self.kernel.get_service(service_name)
                if service:
                    await service.close()  # Awaiting the coroutine
                    return {"status": f"Service {service_name} stopped successfully"}
                else:
                    raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
            except Exception as e:
                logger.error(f"Failed to stop service {service_name}: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to stop service {service_name}")

        @self.app.get('/status')
        async def status():
            return {"status": f"{KERNEL} running" if self.kernel.is_running else "{KERNEL} stopped"}

        @self.app.get('/health')
        async def health():
            try:
                health_report = self.kernel.get_health()
                return {"status": "healthy", "details": health_report.to_dict()}
            except Exception as e:
                logger.error(f"Failed to retrieve health report: {e}")
                raise HTTPException(status_code=500, detail="Failed to retrieve health report")

    async def run_async(self, host, port):
        """Run the server asynchronously."""
        logger.info(f"Starting ZetaZenVm asynchronously on {host}:{port}")
        config = uvicorn.Config(self.app, host=host, port=port, loop="asyncio", log_level="info")
        server = uvicorn.Server(config)
        await server.serve()

    def run(self, host, port):
        """Run the server synchronously."""
        asyncio.run(self.run_async(host, port))

    @staticmethod
    def start_server_request(host, port):
        """Send a request to start the server."""
        start_server_request(host, port)

    @staticmethod
    def check_health(host, port):
        """Send a request to check the health of the server."""
        check_health(host, port)
