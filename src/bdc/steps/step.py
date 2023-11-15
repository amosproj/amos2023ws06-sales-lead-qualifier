# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lucca Baumgärtner <lucca.baumgaertner@fau.de>
from pandas import DataFrame


class StepError(Exception):
    pass


class Step:
    name = None

    def __init__(self) -> None:
        self._df = None

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

    def log(self, message) -> None:
        print(f"[STEP-{self.name.upper()}] - {message}")