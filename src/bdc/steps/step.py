# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lucca Baumgärtner <lucca.baumgaertner@fau.de>
from pandas import DataFrame


class Step:
    name = None

    def __init__(self) -> None:
        self._df = None
        self._input_location = None
        self._output_location = None

    @property
    def df(self) -> DataFrame:
        return self._df

    @df.setter
    def df(self, df) -> None:
        self._df = df

    @property
    def input_location(self) -> str:
        return self._input_location

    @input_location.setter
    def input_location(self, input_location) -> None:
        """
        Set the location for input data. This could be an API endpoint or a CSV file path.
        :param input_location: String file path or API endpoint
        :return:
        """
        self._input_location = input_location

    @property
    def output_location(self) -> str:
        return self._output_location

    @output_location.setter
    def output_location(self, output_location) -> None:
        """
        Set the location for output data. This could be an API endpoint or a CSV file path.
        :param output_location: String file path or API endpoint
        :return:
        """
        self._output_location = output_location

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

    def run(self) -> None:
        """
        Perform the actual processing step.
        """
        raise NotImplementedError

    def finish(self) -> None:
        """
        Finish the execution. Print a report or clean up temporary files.
        """
        raise NotImplementedError

    def log(self, message) -> None:
        print(f"[STEP-{self.name.upper()}] - {message}")
