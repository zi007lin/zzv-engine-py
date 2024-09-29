import sys
import logging

logger = logging.getLogger(__name__)

def handle_critical_error(manager_name: str, error_message: str, exit_code: int = 1):
    """
    Handle critical errors by logging the error and exiting the application.

    Args:
        manager_name (str): The name of the manager encountering the error.
        error_message (str): The error message to log.
        exit_code (int): The exit code for the application. Default is 1.
    """
    logger.error(f"Critical error in {manager_name}: {error_message}")
    logger.error(f"Exiting application with code {exit_code} due to a critical error.")
    sys.exit(exit_code)
