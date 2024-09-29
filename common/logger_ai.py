import atexit
import logging
import os
import socket
import sys

from common.utility import load_logger_config


def init_logger_ai():
    """
    Initialize and configure the root logger for the AI application.
    """
    # Load logger configuration
    try:
        config = load_logger_config()
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

    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers to prevent duplicate logs
    while root_logger.handlers:
        handler = root_logger.handlers.pop()
        handler.close()

    # Set up file and stream handlers
    try:
        file_handler = logging.FileHandler(config.get('log_file', 'application.log'))
        stream_handler = logging.StreamHandler()

        # Configure log handlers with the updated format
        formatter = logging.Formatter(log_format)
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        # Add handlers to the root logger
        root_logger.addHandler(file_handler)
        root_logger.addHandler(stream_handler)

    except Exception as e:
        print(f"Error setting up log handlers: {e}", file=sys.stderr)
        # If setting handlers fails, fallback to basic configuration
        logging.basicConfig(level=log_level, format=log_format)

    # Ensure proper shutdown
    atexit.register(logging.shutdown)
