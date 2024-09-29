# Zeta-Zen VM Project

## Overview
Zeta-Zen VM is a Python-based application with modules for utility functions, custom logging, configuration handling, and testing. It uses a virtual environment for dependency management.

## Project Structure
```
zeta-zen-vm/
├── common/
│   ├── constants.py
│   ├── custom_datetime.py
│   ├── error_handler.py
│   ├── logger_ai.py
│   ├── utility.py
│   └── __init__.py
├── config/
│   ├── logger_config.json
│   └── __init__.py
├── tests/
│   ├── test_common.py
│   ├── test_config.py
│   ├── test_health.py
│   ├── models/
│   │   ├── test_snapshot_parsing.py
│   │   └── __init__.py
│   └── __init__.py
└── proto/
    └── proto-env/
        └── Lib/
```

## Requirements
- Python 3.x
- Virtual environment (venv)

## Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd zeta-zen-vm
   ```
2. Create and activate virtual environment:
   ```bash
   python -m venv proto/proto-env
   source proto/proto-env/bin/activate   # On Windows use `proto\proto-env\Scripts\activate`
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration
Logging configuration is in `config/logger_config.json`. Modify as needed.

## Usage
Run the application:
```bash
python -m zeta-zen-vm
```

## Testing
Run tests using pytest:
```bash
pytest tests/
```

## Modules Description
- **common/**: Utility modules (constants, custom_datetime, logger_ai, etc.)
- **config/**: Configuration files
- **tests/**: Test scripts for each module

## Contributing
Fork the repository, make changes, and submit a pull request. Include test cases for new functionality.

## License
MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
For questions or issues, contact the project maintainers.