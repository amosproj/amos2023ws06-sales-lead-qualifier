# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lucca Baumgärtner <lucca.baumgaertner@fau.de>
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

from pandas import DataFrame

from logger import get_logger

log = get_logger()


class StepError(Exception):
    pass


class Step:
    name: str = None
    added_cols: list[str] = []

    def __init__(self, force_refresh: bool = False) -> None:
        self._df = None
        self._force_refresh = force_refresh

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
            log.warning(
                "Warning trying to check for data presence without setting self.added_cols!",
            )
        if self._force_refresh:
            log.info("Data refresh was forced")
            return False
        data_present = all([col in self._df for col in self.added_cols])
        if data_present:
            log.info(f"Data is present. Not running step.")
        else:
            log.info(f"Data is not present. Fetching through step logic...")
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
