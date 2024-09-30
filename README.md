Here's an updated version of your `README.md` file, incorporating the new directory structure and instructions on how to install the `zzv` package for use in other projects like `zzv-streamer`.

---

# Zeta-Zen VM Project

## Overview
Zeta-Zen VM is a Python-based application with modules for utility functions, custom logging, configuration handling, and testing. It uses a virtual environment for dependency management.

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
│   └── __init__.py
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

## Using the `zzv` Package in Other Projects
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

## Testing
Run tests using pytest:
```bash
pytest tests/
```

## Modules Description
- **zzv/common/**: Utility modules (constants, custom_datetime, logger_ai, etc.)
- **zzv/config/**: Configuration files
- **zzv/msgcore/**: Core messaging and Kafka modules
- **tests/**: Test scripts for each module

## Contributing
Fork the repository, make changes, and submit a pull request. Include test cases for new functionality.

## License
This project is licensed under the Apache License 2.0. See the LICENSE file for details, or view the full license text at https://www.apache.org/licenses/LICENSE-2.0.html.

## Contact
For questions or issues, contact the project maintainers.
