Here is the fully updated `README.md` file:

---

# Zeta-Zen VM Project

## Overview
Zeta-Zen VM is a Python-based application with modules for utility functions, custom logging, configuration handling, and testing. It uses a virtual environment for dependency management and provides a modular architecture for integrating with various external systems like Kafka.

## Project Structure
```
zeta-zen-vm/
├── zzv/
│   ├── common/
│   │   ├── constants.py
│   │   ├── custom_datetime.py
│   │   ├── error_handler.py
│   │   ├── logger_ai.py
│   │   ├── utility.py
│   │   └── __init__.py
│   ├── config/
│   │   ├── logger_config.json
│   │   └── __init__.py
│   ├── engine/
│   │   └── <engine modules>
│   ├── examples/
│   │   └── <example scripts>
│   ├── health/
│   │   └── <health-related modules>
│   ├── models/
│   │   └── <data models>
│   ├── msgcore/
│   │   ├── kafka_consumer.py
│   │   ├── kafka_producer.py
│   │   ├── kafka_producer_consumer.py
│   │   ├── kafka_topic_manager.py
│   │   ├── msg_manager.py
│   │   ├── queue_manager.py
│   │   └── __init__.py
├── tests/
│   ├── test_common.py
│   ├── test_config.py
│   ├── test_health.py
│   ├── models/
│   │   ├── test_snapshot_parsing.py
│   │   └── __init__.py
└── proto/
    ├── snapshot.proto
    └── proto-env/
        └── Lib/
```

## Requirements
- Python 3.x
- Virtual environment (venv)

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd zeta-zen-vm
```

### 2. Create and Activate a Virtual Environment
```bash
python -m venv proto/proto-env
source proto/proto-env/bin/activate   # On Windows use `proto\proto-env\Scripts\activate`
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install the `zzv` Package Locally
To install the `zzv` package for use in other projects like `zzv-streamer`, run the following command from the root of the repository:

```bash
pip install -e .
```

This command installs `zzv` as an editable package, allowing you to make changes to the `zzv` source code and have them reflected immediately without reinstallation.

### 5. Using the `zzv` Package in Other Projects
Once installed, you can import and use `zzv` in other Python projects as follows:

```python
from zzv.common import logger_ai
from zzv.msgcore import kafka_producer, kafka_consumer
```

You can now build projects like `zzv-streamer` that depend on the `zzv` package.

## Configuration
Logging configuration is located in `config/logger_config.json`. Modify it as needed.

## Usage
To run the application:
```bash
python -m zeta-zen-vm
```

## Building the Project as an Executable

### Using PyInstaller (Recommended)

`PyInstaller` is a tool that bundles a Python application and all its dependencies into a single package. This allows you to distribute the project as a standalone executable.

#### Windows

1. **Install PyInstaller:**

   ```bash
   pip install pyinstaller
   ```

2. **Build the Executable:**

   Run the following command from the root directory of the project:

   ```bash
   pyinstaller --onefile --name zzv --distpath dist --paths . --hidden-import zzv zzv/examples/basic_usage.py
   ```

   - `--onefile`: Creates a single standalone executable.
   - `--name zzv`: Sets the name of the executable to `zzv`.
   - `--distpath dist`: Outputs the executable to the `dist/` directory.
   - `zzv/examples/basic_usage.py`: The path to the script you want to convert into an executable.

3. **Copy Configuration Directory:**

   After building the executable, copy the `config` directory to the `dist` directory as follows:

   ```
   cp -r zeta-zen-vm/config dist/config
   ```

   This step is crucial as the application requires configuration files located in the `config` directory to run properly.

4. **Run the Executable:**

   After copying the configuration directory, you can run the `zzv.exe` file inside the `dist/` directory:

   ```bash
   dist/zzv.exe
   ```

#### Linux and macOS

1. **Install PyInstaller:**

   ```bash
   pip install pyinstaller
   ```

2. **Build the Executable:**

   Run the following command:

   ```bash
   pyinstaller --onefile --name zzv --distpath dist --paths . --hidden-import zzv zzv/examples/basic_usage.py
   ```

3. **Copy Configuration Directory:**

   After building the executable, copy the `config` directory to the `dist` directory as follows:

   ```bash
   cp -r zeta-zen-vm/config dist/config
   ```

4. **Run the Executable:**

   On Linux and macOS, the executable will be named `zzv` (without the `.exe` extension). Navigate to the `dist` directory and run:

   ```bash
   ./dist/zzv
   ```

### Accessing the Swagger UI

After starting the application, you can access the Swagger UI to test the API endpoints:

1. Open a browser and navigate to:

   ```
   http://localhost:8000/docs
   ```

2. You should see a Swagger UI interface that allows you to interact with the API. For example, you can test the health check endpoint (`/health`) by clicking on it and then clicking the `Try it out` button.

**Example Output:**
```
2024-09-30 00:33:06,851 - DESKTOP-P1JOHD2 - INFO - Starting the server based on the configuration...
2024-09-30 00:33:06,853 - DESKTOP-P1JOHD2 - INFO - Engine started in a separate thread.
2024-09-30 00:33:06,854 - DESKTOP-P1JOHD2 - INFO - Starting ZetaZenVm asynchronously on 0.0.0.0:8000
INFO:     Started server process [26556]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:54608 - "POST /start HTTP/1.1" 200 OK
INFO:     127.0.0.1:54611 - "GET /health HTTP/1.1" 200 OK
Health check successful: {'status': 'healthy', 'details': {'manager_name': 'Kernel', 'status': 'OK', 'details': ['QueueManager is healthy', 'Messages in queue: 0', 'Messages enqueued: 0', 'Messages processed: 0', 'Messages sent: 0', 'MsgManager is healthy', 'ExampleManager health check successful']}}
```
Based on the existing `logger_ai.py` file, I'll modify it to dynamically generate the log filename based on the package name and include an optional `logs_root_dir` parameter. Then, I'll update the `README.md` file to reflect these changes.

### Modified `logger_ai.py`

Here's the updated `logger_ai.py` file with the new functionality:

```python
import atexit
import logging
import os
import socket
import sys
from datetime import datetime
from zzv.common.utility import load_logger_config


def init_logger_ai(package_name: str = None, logs_root_dir: str = None):
    """
    Initialize and configure the root logger for the AI application.

    :param package_name: Name of the package to use in the log filename, defaults to the current directory name.
    :param logs_root_dir: Root directory for logs. If None, defaults to '../../logs'.
    :return: Configured logger
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

    # Set up file and stream handlers
    try:
        file_handler = logging.FileHandler(log_file_path)
        stream_handler = logging.StreamHandler()

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


# Example usage:
# Initialize the logger with the package name as "zzv" and logs_root_dir as None (default to "../../logs")
logger = init_logger_ai(package_name="zzv")
logger.info("Logger initialized successfully.")
```

## Logging Configuration

### Configuring Log Files

The `logger_ai.py` script initializes and configures logging for the application. By default, log files will be created in the `../../logs` directory (relative to the script's location) and named using the format:

```
<package_name>-YYYY-MM-DDTHH-MM-SS.log
```

#### Parameters for `init_logger_ai` Function:

- **`package_name`**:  
  Name of the package to use in the log filename. If not provided, it defaults to the current working directory name.

- **`logs_root_dir`**:  
  Root directory for logs. If not provided, it defaults to `../../logs`. This parameter allows you to customize where the logs are saved.

### Example Usage:

1. **Using Default Settings**:

   ```python
   from logger_ai import init_logger_ai
   logger = init_logger_ai(package_name="zzv")
   logger.info("Default logger initialized successfully.")
   ```

   The logs will be saved in the `../../logs` directory with filenames like:

   ```
   ../../logs/zzv-2024-10-01T12-30-00.log
   ```

2. **Specifying a Custom Logs Directory**:

   ```python
   logger = init_logger_ai(package_name="zzv-streamer-py", logs_root_dir="/var/logs/zzv-streamer")
   logger.info("Logger with custom logs directory initialized successfully.")
   ```

   The logs will be saved in the `/var/logs/zzv-streamer` directory with filenames like:

   ```
   /var/logs/zzv-streamer/zzv-streamer-py-2024-10-01T12-30-00.log
   ```

3. **Relative Logs Directory**:

   ```python
   logger = init_logger_ai(package_name="zzv", logs_root_dir="relative/logs/path")
   logger.info("Logger with relative logs directory initialized successfully.")
   ```

   The logs will be saved in the `relative/logs/path` directory relative to the current working directory.

### Setting Log Levels
You can specify the log level using the `LOG_LEVEL` environment variable or by setting it in the configuration file. The log levels can be set to `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`.

### Log Format
The log format includes the following fields:

```
%(asctime)s - %(hostname)s - %(name)s - %(levelname)s - %(message)s
```

- `%(asctime)s`: Timestamp of the log entry.
- `%(hostname)s`: Hostname of the machine running the application.
- `%(name)s`: Name of the logger or module.
- `%(levelname)s`: Log level (INFO, DEBUG, etc.).
- `%(message)s`: Log message content.

These fields can be customized in the configuration file (`logger_config.json`) or directly in the script.

### Additional Options for Building
- To include additional directories or modules, use the `--add-data` or `--hidden-import` options:

  ```bash
  pyinstaller --onefile --name zzv --distpath dist --add-data "zzv/config:zzv/config" --hidden-import "zzv.common" zzv/examples/basic_usage.py
  ```

## Version Management and Package Updates

### 1. Update the `zzv` Package Version
Whenever you make changes or add new functionality, update the `version` field in the `setup.py` file:

```python
setup(
    name='zzv',
    version='0.2.0',  # Increment the version number
    # Other setup configurations...
)
```

### 2. Reinstall the Updated Package
After updating the `setup.py` file, reinstall the `zzv` package:

```bash
pip uninstall zzv
pip install -e .
```

This ensures that the new version of `zzv` is installed in your environment.

### 3. Pull the New Version in Dependent Projects
If you’re using `zzv` in other projects like `zzv-streamer`, upgrade to the latest version:

1. **If using a direct path:**

   ```bash
   pip install -e /path/to/updated/zzv
   ```

2. **If `zzv` is hosted in a repository or PyPI:**

   ```bash
   pip install --upgrade zzv
   ```

### 4. Publish to PyPI (Optional)
To publish a new version to PyPI:

1. Update `version` in `setup.py`.
2. Build the package:

   ```bash
   python setup.py sdist bdist

_wheel
   ```

3. Upload using `twine`:

   ```bash
   twine upload dist/*
   ```

Ensure `twine` is installed:

```bash
pip install twine
```

This makes the new version available on PyPI for use in other projects.

## Modules Description

### `zzv/`
The main package that contains all the core modules, utilities, configuration handlers, and services for the Zeta-Zen VM project.

- **`zzv.common/`**:  
  This sub-package provides common utility functions and constants used across the application. It acts as a shared resource for other modules.

  - `constants.py`: Defines global constants that are used throughout the project.
  - `custom_datetime.py`: Contains custom date and time utilities for handling various datetime operations.
  - `error_handler.py`: Provides a centralized error handling mechanism, including custom exceptions and error logging.
  - `logger_ai.py`: Implements advanced logging functionality, which can be extended to include logging to files, streams, or external monitoring services.
  - `utility.py`: General-purpose utility functions, such as file operations, configuration handling, and common data transformations.

- **`zzv.config/`**:  
  Contains configuration-related modules for managing the application’s settings and logging configurations.

  - `logger_config.json`: Configuration file for setting up logging options and formats.
  - `__init__.py`: Initializes the `config` package.

- **`zzv.engine/`**:  
  The core engine of the project that manages services and controls the lifecycle of the application.

  - `kernel.py`: Manages the registration and execution of services. Handles starting and stopping of the kernel.
  - `kernel_config.py`: Contains configuration settings specific to the kernel, such as service registrations and dependency management.
  - `manager.py`: Defines a base `Manager` class, which all service managers in the application inherit from. Provides start, stop, and health-check methods.
  - `zeta_zen_vm.py`: The main entry point for running the application, initializing the kernel, and starting up the various services.

- **`zzv.examples/`**:  
  Contains example scripts and usage scenarios to demonstrate how to interact with various modules in the project.

  - `basic_usage.py`: Provides an example of basic usage of core functionalities in the `zzv` package.
  - `example_manager.py`: Demonstrates how to create a custom service manager and register it with the kernel.

- **`zzv.health/`**:  
  Modules related to monitoring and health-checks of the services within the application.

  - `health.py`: Implements health-check mechanisms for different components of the application.
  - `health_report.py`: Collects health metrics and reports the status of various services.
  - `status.py`: Defines the different health statuses (e.g., UP, DOWN, MAINTENANCE).

- **`zzv.models/`**:  
  Data models and schemas used for representing the data processed within the application.

  - `snapshot.py`: Data model for snapshot-related data, such as timestamped snapshots of system states.
  - `__init__.py`: Initializes the `models` package.

- **`zzv.msgcore/`**:  
  Core messaging and Kafka-related modules that handle message production, consumption, and management.

  - `kafka_consumer.py`: Implements a Kafka consumer to read messages from Kafka topics and process them.
  - `kafka_producer.py`: Provides a Kafka producer to send messages to Kafka topics.
  - `kafka_producer_consumer.py`: Combines the functionality of both producer and consumer to enable bidirectional messaging.
  - `kafka_topic_manager.py`: Manages Kafka topics, including creation, deletion, and partition management.
  - `msg_manager.py`: General message management functionalities, such as queue handling and message parsing.
  - `queue_manager.py`: Implements a queue manager to handle message queues within the application.
  - **`transporters/`**:  
    - `kafka_transporter.py`: Provides a specific transporter implementation using Kafka as the underlying message broker.

- **`zzv.proto/`**:  
  Contains Protocol Buffer (.proto) files and generated code for handling serialized data structures.

  - `snapshot.proto`: Defines the structure of snapshot-related messages exchanged between services.
  - `proto-env/`: Contains environment-specific files and libraries for working with Protocol Buffers.

- **`zzv.tests/`**:  
  Contains test scripts for verifying the functionality of each module.

  - `test_common.py`: Tests for the `common` package, including utility functions and constants.
  - `test_config.py`: Tests for configuration handling and loading.
  - `test_health.py`: Tests for health-check modules.
  - **`models/`**:  
    - `test_snapshot_parsing.py`: Tests for the `snapshot` data model, ensuring correct parsing and validation.

## Contributing
Fork the repository, make changes, and submit a pull request. Include test cases for new functionality.

## License
This project is licensed under the Apache License 2.0. See the LICENSE file for details, or view the full license text at https://www.apache.org/licenses/LICENSE-2.0.html.

## Contact
For questions or issues, contact the project maintainers.
