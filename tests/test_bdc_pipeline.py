# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lucca Baumgärtner <lucca.baumgaertner@fau.de>
import os
import unittest
from unittest import mock

import pandas as pd
from pandas import DataFrame

from bdc.pipeline import Pipeline
from bdc.steps.step import Step
from database.leads import decode_s3_url


class DummyStepOne(Step):
    name = "Dummy_Step_One"
    added_cols = ["TestCol"]

    def load_data(self) -> None:
        pass

    def verify(self) -> bool:
        return True

    def check_data_presence(self) -> bool:
        return False

    def run(self) -> DataFrame:
        return pd.DataFrame()

    def finish(self) -> None:
        pass


class DummyStepTwo(Step):
    name = "Dummy_Step_Two"
    added_cols = ["TestCol"]

    def load_data(self) -> None:
        self.df = pd.DataFrame(columns=["TestCol"])

    def verify(self) -> bool:
        return True

    def check_data_presence(self) -> bool:
        return super().check_data_presence()

    def run(self) -> DataFrame:
        return pd.DataFrame()

    def finish(self) -> None:
        pass


class TestPipelineFramework(unittest.TestCase):
    p_one: Pipeline
    p_two: Pipeline
    dummy_step_one: Step
    dummy_step_two: Step
    dummy_step_three: Step

    def setUp(self):
        os.environ["DATABASE_TYPE"] = "Local"
        self.dummy_step_one = DummyStepOne()
        self.dummy_step_two = DummyStepTwo()
        self.dummy_step_three = DummyStepTwo(force_refresh=True)
        # create pipeline without actually reading from a csv file
        with mock.patch(
            "database.leads.repository.Repository.__init__"
        ) as init_db_mock, mock.patch(
            "database.leads.repository.Repository.get_dataframe"
        ):
            init_db_mock.return_value = None
            self.p_one = Pipeline([self.dummy_step_one], limit=10)
            self.p_two = Pipeline(
                [self.dummy_step_two, self.dummy_step_three], limit=10
            )

    def test_verify(self):
        with (
            mock.patch.object(self.dummy_step_one, "load_data") as load_data_mock,
            mock.patch.object(self.dummy_step_one, "verify") as verify_mock,
            mock.patch.object(
                self.dummy_step_one, "check_data_presence"
            ) as check_data_presence_mock,
            mock.patch.object(self.dummy_step_one, "run") as run_mock,
            mock.patch.object(self.dummy_step_one, "finish") as finish_mock,
        ):
            check_data_presence_mock.return_value = False
            verify_mock.return_value = True

            self.p_one.run()

            load_data_mock.assert_called_once()
            verify_mock.assert_called_once()
            check_data_presence_mock.assert_called_once()
            run_mock.assert_called_once()
            finish_mock.assert_called_once()

    def test_verify_fails(self):
        with (
            mock.patch.object(self.dummy_step_one, "load_data") as load_data_mock,
            mock.patch.object(self.dummy_step_one, "verify") as verify_mock,
            mock.patch.object(
                self.dummy_step_one, "check_data_presence"
            ) as check_data_presence_mock,
            mock.patch.object(self.dummy_step_one, "run") as run_mock,
            mock.patch.object(self.dummy_step_one, "finish") as finish_mock,
        ):
            # make verify() return false
            verify_mock.return_value = False

            # run pipeline
            self.p_one.run()

            # assert that all methods were run except for run() and check_data_presence()
            load_data_mock.assert_called_once()
            verify_mock.assert_called_once()
            check_data_presence_mock.assert_called_once()
            run_mock.assert_not_called()
            finish_mock.assert_not_called()

    def test_data_presence(self):
        with (
            mock.patch.object(self.dummy_step_two, "verify") as verify_mock_two,
            mock.patch.object(self.dummy_step_two, "run") as run_mock_two,
            mock.patch.object(self.dummy_step_two, "finish") as finish_mock_two,
            mock.patch.object(self.dummy_step_three, "verify") as verify_mock_three,
            mock.patch.object(self.dummy_step_three, "run") as run_mock_three,
            mock.patch.object(self.dummy_step_three, "finish") as finish_mock_three,
        ):
            verify_mock_two.return_value = True
            verify_mock_three.return_value = True

            self.p_two.run()

            verify_mock_two.assert_called_once()
            verify_mock_three.assert_called_once()

            run_mock_two.assert_not_called()
            run_mock_three.assert_called_once()

            finish_mock_two.assert_not_called()
            finish_mock_three.assert_called_once()


class TestS3Utils(unittest.TestCase):
    def test_s3_url_decoder(self):
        bucket = "amos--data--events"
        key = "leads/enriched.csv"
        url = f"s3://{bucket}/{key}"

        actual_bucket, actual_key = decode_s3_url(url)
        self.assertEqual(bucket, actual_bucket)
        self.assertEqual(key, actual_key)


if __name__ == "__main__":
    unittest.main()
