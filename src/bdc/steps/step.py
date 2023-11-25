# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lucca Baumgärtner <lucca.baumgaertner@fau.de>
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

from enum import Enum

from pandas import DataFrame

RED = "\033[91m"
BLUE = "\033[34m"
YELLOW = "\033[93m"
RESET = "\033[0m"


class LogLevel(Enum):
    info = "info"
    warning = "warning"
    error = "error"


class StepError(Exception):
    pass


class Step:
    name: str = None
    added_cols: list[str] = []

    def __init__(self, force_execution: bool = False) -> None:
        self._df = None
        self._force_execution = force_execution

    @property
    def df(self) -> DataFrame:
        return self._df

    @df.setter
    def df(self, df) -> None:
        self._df = df

    def load_data(self) -> None:
        """
        Load data for this processing step. This could be an API call or reading from a CSV file. Can also be empty
        if self.df is used.
        """
        raise NotImplementedError

    def verify(self) -> bool:
        """
        Verify that the data has been loaded correctly and is present in a format that can be processed by this step.
        """
        raise NotImplementedError

    def check_data_presence(self) -> bool:
        """
        Check whether the data this step collects is already present in the df.
        Can be forced to return False if self._force_execution is set to True.
        """
        if len(self.added_cols) == 0:
            self.log(
                "Warning trying to check for data presence without setting self.added_cols!",
                level=LogLevel.warning,
            )
        if self._force_execution:
            self.log("Fetching data was forced")
            return False
        data_present = all([col in self._df for col in self.added_cols])
        if data_present:
            self.log(f"Data is present. Not running step.")
        else:
            self.log(f"Data is not present. Fetching through step logic...")
        return all([col in self._df for col in self.added_cols])

    def run(self) -> DataFrame:
        """
        Perform the actual processing step.

        raises StepError
        """
        raise NotImplementedError

    def finish(self) -> None:
        """
        Finish the execution. Print a report or clean up temporary files.
        """
        raise NotImplementedError

    def log(self, message, level=LogLevel.info) -> None:
        if level == LogLevel.info:
            print(f"[STEP-{self.name.upper()}] - " + BLUE + f"{message}" + RESET)
        if level == LogLevel.warning:
            print(f"[STEP-{self.name.upper()}] - " + YELLOW + f"{message}" + RESET)
        if level == LogLevel.error:
            print(f"[STEP-{self.name.upper()}] - " + RED + f"{message}" + RESET)
