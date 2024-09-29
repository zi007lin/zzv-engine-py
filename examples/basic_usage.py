# examples/basic_usage.py

"""
Basic Usage Example for Zeta Zen Vm with ExampleManager and Configuration File

This script demonstrates how to set up and run `Zeta Zen Vm` using an `ExampleManager` and a configuration file.
The server is started in a separate thread, and the script sends start and health check requests to ensure
the services are running correctly.

Prerequisites:
1. Ensure that `config/basic_usage_config.yaml` exists with the necessary configuration.
2. Make sure `example_manager.py` is implemented and placed in the `examples` folder.

How to Run:
1. Navigate to the root directory of the project.
2. Run the script using the following command:
3. Open your browser and navigate to `http://127.0.0.1:8000/docs` to view the Swagger UI documentation.

Components Demonstrated:
- `ZetaZenVm`: The main server-side application class that initializes and runs the server.
- `ExampleManager`: A basic manager with custom endpoints to demonstrate manager integration.
- FastAPI: The web framework used to create REST API endpoints and serve the application.
"""

import logging
import os
import sys
import time
from threading import Thread

from common.logger_ai import init_logger_ai  # Ensure this module is in the correct location
from common.utility import load_config, should_start_server  # Ensure utility module is available
from engine.zeta_zen_vm import ZetaZenVm
from examples.example_manager import ExampleManager  # Import the ExampleManager

logger = logging.getLogger(__name__)

def main():
 """
 Main function to start Zeta Zen Vm with threading.
 This function initializes the logger, loads the configuration, and starts the server in a separate thread.
 """
 # Step 1: Initialize the logger
 init_logger_ai()
 logger.info(f"Python version: {sys.version}, Platform: {sys.platform}")

 # Step 2: Load the configuration from the YAML file
 config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'basic_usage_config.yaml')
 config = load_config(config_path)
 host = config['server']['host']
 port = config['server']['port']

 # Step 3: Create an instance of the ExampleManager
 example_manager_instance = ExampleManager()

 # Step 4: Create an instance of ZetaZenVm with the loaded configuration and the ExampleManager
 engine = ZetaZenVm(config=config, additional_managers=[{"name": "ExampleManager", "instance": example_manager_instance}])

 # Step 5: Check if the server should start automatically based on the configuration
 if should_start_server():
     logger.info("Starting the server based on the configuration...")

     # Step 6: Start the engine in a separate thread to allow concurrent operations
     engine_thread = Thread(target=engine.run, kwargs={'host': host, 'port': port})
     engine_thread.start()
     logger.info("Engine started in a separate thread.")

     # Step 7: Wait for a brief period to ensure the server is up and running
     time.sleep(2)

     # Step 8: Send a server start request using the static method
     ZetaZenVm.start_server_request(host, port)
     time.sleep(1)

     # Step 9: Perform a health check to verify that the server is functioning correctly
     ZetaZenVm.check_health(host, port)

if __name__ == "__main__":
 # Run the main function if the script is executed directly
 main()
