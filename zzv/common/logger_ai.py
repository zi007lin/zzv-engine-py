import atexit
import logging
import os
import socket
import sys
from datetime import datetime

from common.utility import load_logger_config


def init_logger_ai(package_name: str = None, logs_root_dir: str = None, logger_config_path: str = None):
    """
    Initialize and configure the root logger for the AI application.

    :param package_name: Name of the package to use in the log filename, defaults to the current directory name.
    :param logs_root_dir: Root directory for logs. If None, defaults to '../../logs'.
    :param logger_config_path: Path to the logger configuration file.
    :return: Configured logger
    """
    # Load logger configuration
    try:
        config = load_logger_config(config_path=logger_config_path)
    except Exception as e:
        # Fallback to default configuration if loading fails
        print(f"Error loading logger configuration: {e}", file=sys.stderr)
        config = {
            'log_format': '%(asctime)s - %(hostname)s - %(name)s - %(levelname)s - %(message)s',
            'log_file': 'application.log',
            'log_level': 'INFO',
        }

    # Get the hostname
    hostname = socket.gethostname()

    # Update the log format with the hostname
    log_format = config.get('log_format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_format = log_format.replace('%(hostname)s', hostname)

    # Set log level from environment variable or default to the config file setting
    log_level_str = os.getenv('LOG_LEVEL', config.get('log_level', 'INFO')).upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    # Determine the package name and log file name
    base_dir_name = os.path.basename(os.getcwd()) if not package_name else package_name

    # Determine the logs root directory
    if logs_root_dir is None:
        logs_root_dir = os.path.abspath(os.path.join(os.getcwd(), "../../logs"))
    else:
        logs_root_dir = os.path.abspath(logs_root_dir)

    # Create the logs directory if it doesn't exist
    if not os.path.exists(logs_root_dir):
        os.makedirs(logs_root_dir)

    # Define the dynamic filename based on the current timestamp and package name
    log_filename = f"{base_dir_name}-{datetime.now().strftime('%Y-%m-%dT%H-%M-%S')}.log"
    log_file_path = os.path.join(logs_root_dir, log_filename)

    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers to prevent duplicate logs
    while root_logger.handlers:
        handler = root_logger.handlers.pop()
        handler.close()

    # Set up file and stream handlers with UTF-8 support
    try:
        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        stream_handler = logging.StreamHandler(sys.stdout)
        # Set stream handler to use UTF-8 encoding
        stream_handler.stream = open(sys.stdout.fileno(), 'w', encoding='utf-8', buffering=1)

        # Configure log handlers with the updated format
        formatter = logging.Formatter(log_format)
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        # Add handlers to the root logger
        root_logger.addHandler(file_handler)
        root_logger.addHandler(stream_handler)

        # Print the log file path for confirmation
        root_logger.info(f"Logging to file: {log_file_path}")

    except Exception as e:
        print(f"Error setting up log handlers: {e}", file=sys.stderr)
        # If setting handlers fails, fallback to basic configuration
        logging.basicConfig(level=log_level, format=log_format)

    # Ensure proper shutdown
    atexit.register(logging.shutdown)

    return root_logger
