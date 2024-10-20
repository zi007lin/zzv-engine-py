import csv
import io
import json
import os
import shutil
import socket
import time
from io import BytesIO

import requests  # Add requests for HTTP operations
import yaml  # Add yaml for configuration handling
import logging

logger = logging.getLogger(__name__)


# Assuming COMMON_ROOT is defined somewhere globally, or you can define it here
COMMON_ROOT = os.path.dirname(os.path.abspath(__file__))


def clean_directory(directory_path):
    """Removes all files in the specified directory."""
    if os.path.exists(directory_path):
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
    else:
        print(f"Directory {directory_path} does not exist. No cleaning needed.")


def convert_image_to_bytes(img):
    """Convert image to bytes."""
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_bytes = img_byte_arr.getvalue()
    return img_bytes


def get_keys_path(keys_file):
    keys_path = os.path.join(COMMON_ROOT, '..', '..', 'user_keys', keys_file)
    return keys_path


def generate_config_filename(tag_name: str) -> str:
    """
    Generate a configuration filename based on the hostname and tag name.

    Args:
        tag_name (str): The tag name to include in the configuration filename.

    Returns:
        str: The generated configuration filename.
    """
    hostname = socket.gethostname()
    config_filename = f"{hostname}_{tag_name}"
    return config_filename


def get_default_config_path(tag_name: str) -> str:
    """
    Get the default configuration path for the given tag name.

    Args:
        tag_name (str): The tag name to include in the configuration filename.

    Returns:
        str: The full path to the configuration file.
    """
    config_filename = generate_config_filename(tag_name)
    config_path = os.path.join(COMMON_ROOT, '..', 'config', config_filename)
    return config_path


def load_agent_config(tag_name=None, config_path=None):
    if tag_name is not None:
        config_path = get_default_config_path(tag_name)

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, 'r') as file:
        config = json.load(file)

    config['config_path'] = config_path
    return config


def ensure_screenshot_directory_exists(group_name, custom_datetime, directory_path=None):
    """Ensure screenshot directory exists."""
    today_date = custom_datetime.now().strftime('%Y%m%d')
    if directory_path is None:
        directory_path = os.path.join(COMMON_ROOT, '..', '..', 'data', group_name, today_date)

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Directory created: {directory_path}")
    return directory_path


def load_logger_config(config_path=None):
    if config_path is None:
        config_path = '../../config/logger_config.json'

    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            config = json.load(file)
    else:
        config = {
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'log_format': os.getenv('LOG_FORMAT', '%(asctime)s - %(hostname)s - %(levelname)s - %(message)s'),
            'log_file': os.getenv('LOG_FILE', 'app.log')
        }
    return config


def split_numeric_and_string(data):
    """Splits numeric and string components."""
    result = []
    for item in data:
        parts = item.split(' ', 1)
        if len(parts) == 2:
            try:
                numeric_part = float(parts[0])
                string_part = parts[1]
                result.extend([numeric_part, string_part])
            except ValueError:
                result.append(item)
        else:
            result.append(item)
    return result


def format_elapsed_time(start_time_ns: int) -> (str, float):
    """Calculate elapsed time from start_time and format it to a readable string."""
    elapsed_time_ns = time.perf_counter_ns() - start_time_ns
    seconds, nanoseconds = divmod(elapsed_time_ns, 1_000_000_000)
    milliseconds = nanoseconds // 1_000_000
    microseconds = (nanoseconds % 1_000_000) // 1_000
    nanoseconds = nanoseconds % 1_000
    elapsed_time_ns_formatted = f"{seconds}s {milliseconds}ms {microseconds}us {nanoseconds}ns"
    return elapsed_time_ns_formatted, elapsed_time_ns


# New Utility Functions for Server Control

def load_config(config_path='config/config.yaml'):
    """Load the server configuration from a YAML file."""
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config


def translate_host_for_requests(host):
    """Translate the host address for HTTP requests."""
    return "localhost" if host == "0.0.0.0" else host


def start_server_request(host, port):
    """
    Function to send a request to start the Virtual Voyage Server.
    """
    host_for_request = translate_host_for_requests(host)
    try:
        response = requests.post(f"http://{host_for_request}:{port}/start")
        if response.status_code == 200:
            print(f"Server started successfully on {host}:{port}.")
        else:
            print(f"Failed to start server. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while starting the server: {e}")


def check_health(host, port):
    """
    Function to check the health of the server.
    """
    host_for_request = translate_host_for_requests(host)
    try:
        response = requests.get(f"http://{host_for_request}:{port}/health")
        if response.status_code == 200:
            print("Health check successful: " + str(response.json()))
        else:
            print(f"Health check failed. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during health check: {e}")


def should_start_server():
    """
    Determine whether the server should be started based on configuration or other conditions.

    This function can be modified to include more complex logic, such as checking environment variables,
    configuration flags, or other preconditions required before starting the server.

    Returns:
        bool: True if the server should start, False otherwise.
    """
    # Example condition: Check an environment variable or a configuration flag
    start_server = os.getenv('START_SERVER', 'true').lower() == 'true'

    # Example condition: Check for the existence of a file that indicates server should start
    # start_server = os.path.exists('/path/to/start_server_flag_file')

    # Modify the logic here based on your specific requirements.
    return start_server


def load_config_from_bytes(config_bytes: bytes, format: str = 'yaml') -> dict:
    """
    Load the configuration from a byte stream.

    Args:
        config_bytes (bytes): The configuration data in bytes format.
        format (str): The format of the configuration file ('yaml' or 'json').

    Returns:
        dict: The parsed configuration dictionary.
    """
    config_stream = io.BytesIO(config_bytes)
    if format.lower() == 'yaml':
        config = yaml.safe_load(config_stream)
    elif format.lower() == 'json':
        import json
        config = json.load(config_stream)
    else:
        raise ValueError("Unsupported configuration format. Supported formats: 'yaml', 'json'.")

    return config

def print_snapshots_as_csv(json_string):
    # Parse the JSON string
    data = json.loads(json_string)

    # Extract the snapshots
    snapshots = data.get('snapshots', [])

    # Prepare CSV output
    output = io.StringIO()

    # Determine fieldnames (assuming all snapshots have the same structure)
    if snapshots:
        fieldnames = list(snapshots[0].keys())
    else:
        print("No snapshots found in the data.")
        return

    # Create CSV writer
    writer = csv.DictWriter(output, fieldnames=fieldnames)

    # Write header
    writer.writeheader()

    # Write rows
    for snapshot in snapshots:
        writer.writerow(snapshot)

    # Print the CSV data
    logger.info(output.getvalue())