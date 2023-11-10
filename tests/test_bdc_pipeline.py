# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lucca Baumgärtner <lucca.baumgaertner@fau.de>

import unittest
from unittest import mock

import pandas as pd
from pandas import DataFrame

from bdc.pipeline import Pipeline
from bdc.steps.step import Step


class DummyStepOne(Step):
    name = "Dummy_Step_One"

    def load_data(self) -> None:
        pass

    def verify(self) -> bool:
        return True

    def run(self) -> DataFrame:
        return pd.DataFrame()

    def finish(self) -> None:
        pass


class TestPipelineFramework(unittest.TestCase):
    p: Pipeline
    dummy_step_one: Step

    def setUp(self):
        self.dummy_step_one = DummyStepOne()
        # create pipeline without actually reading from a csv file
        with mock.patch("pandas.read_csv") as read_csv_mock:
            self.p = Pipeline([self.dummy_step_one], "./not_valid.csv")
            read_csv_mock.assert_called_with("./not_valid.csv")

    def test_verify(self):
        with (
            mock.patch.object(self.dummy_step_one, "load_data") as load_data_mock,
            mock.patch.object(self.dummy_step_one, "verify") as verify_mock,
            mock.patch.object(self.dummy_step_one, "run") as run_mock,
            mock.patch.object(self.dummy_step_one, "finish") as finish_mock,
        ):
            self.p.run()
            load_data_mock.assert_called_once()
            verify_mock.assert_called_once()
            run_mock.assert_called_once()
            finish_mock.assert_called_once()

    def test_verify_fails(self):
        with (
            mock.patch.object(self.dummy_step_one, "load_data") as load_data_mock,
            mock.patch.object(self.dummy_step_one, "verify") as verify_mock,
            mock.patch.object(self.dummy_step_one, "run") as run_mock,
            mock.patch.object(self.dummy_step_one, "finish") as finish_mock,
        ):
            # make verify() return false
            verify_mock.return_value = False

            # run pipeline
            self.p.run()

            # assert that all methods were run except for run()
            load_data_mock.assert_called_once()
            verify_mock.assert_called_once()
            run_mock.assert_not_called()
            finish_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
