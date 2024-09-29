from datetime import datetime

from common.custom_datetime import CustomDateTime, KERNEL_MODE_SIMULATED

# Kernel Configuration
# Set up the mode and simulated datetime (if needed)
SIMULATED_DATETIME = datetime(2024, 8, 23, 15, 35, 6)  # Example simulated datetime

# Initialize the custom datetime class for use globally
custom_datetime = CustomDateTime(mode=KERNEL_MODE_SIMULATED, simulated_datetime=SIMULATED_DATETIME)
