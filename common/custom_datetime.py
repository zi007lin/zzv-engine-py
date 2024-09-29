from datetime import datetime, timedelta

KERNEL_MODE_SIMULATED = 'SIMULATED'  # or 'REAL-TIME'
KERNEL_MODE_REALTIME = 'REAL-TIME'


class CustomDateTime:
    def __init__(self, mode=KERNEL_MODE_REALTIME, simulated_datetime=None):
        """
        Initialize the CustomDateTime class.

        :param mode: Mode of operation ('REAL-TIME' or 'SIMULATED').
        :param simulated_datetime: The datetime to simulate if mode is 'SIMULATED'.
        """
        self.mode = mode
        if mode == 'SIMULATED' and simulated_datetime is not None:
            self.simulated_datetime = simulated_datetime
        else:
            self.simulated_datetime = None

    def now(self):
        """
        Get the current datetime based on the mode.

        :return: Current datetime object.
        """
        if self.mode == 'SIMULATED' and self.simulated_datetime is not None:
            return self.simulated_datetime
        else:
            return datetime.now()

    def advance_time(self, delta: timedelta):
        """
        Advance the simulated time by a given timedelta.

        :param delta: timedelta object to add to the simulated time.
        """
        if self.mode == 'SIMULATED' and self.simulated_datetime is not None:
            self.simulated_datetime += delta
        else:
            raise ValueError("Time can only be advanced in SIMULATED mode with a valid simulated_datetime.")
