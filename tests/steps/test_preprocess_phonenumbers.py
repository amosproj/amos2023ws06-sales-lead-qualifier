# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 Felix Zailskas <felixzailskas@gmail.com>

import unittest
from unittest.mock import patch

import pandas as pd

from bdc.steps.helpers.generate_hash_leads import LeadHashGenerator
from bdc.steps.preprocess_phonenumbers import PreprocessPhonenumbers
from tests import mock_hash_check


class TestStepExecution(unittest.TestCase):
    def setUp(self):
        self.lead_data = {
            "First Name": ["John"] * 7,
            "Last Name": ["Doe"] * 7,
            "Phone": [
                "4930183992170",
                "invalid_phone",
                "442087599036",
                "3197010281402",
                "436601359011",
                "33757056600",
                "495111233421",
            ],
        }
        self.step = PreprocessPhonenumbers(force_refresh=True)
        self.step.df = pd.DataFrame(self.lead_data)
        self.formatted_gt = [
            "+49 30 183992170",
            "",
            "+44 20 8759 9036",
            "+31 970 102 81402",
            "+43 660 1359011",
            "+33 7 57 05 66 00",
            "+49 511 1233421",
        ]
        self.country_gt = [
            "Germany",
            "",
            "United Kingdom",
            "Netherlands",
            "Austria",
            "France",
            "Germany",
        ]
        self.area_gt = [
            "Berlin",
            "",
            "London",
            "",
            "",
            "",
            "Hannover",
        ]
        self.valid_gt = [
            True,
            False,
            True,
            True,
            True,
            True,
            True,
        ]
        self.possible_gt = [
            True,
            False,
            True,
            True,
            True,
            True,
            True,
        ]

    @patch.object(LeadHashGenerator, "hash_check", mock_hash_check)
    def test_hash_lead(self):
        result = self.step.run()

        assert type(result) is pd.DataFrame
        columns = result.columns.to_list()
        assert all(
            col in columns
            for col in [
                "First Name",
                "Last Name",
                "Phone",
                "number_formatted",
                "number_country",
                "number_area",
                "number_valid",
                "number_possible",
            ]
        )
        # test formatted number
        for test, gt in zip(result["number_formatted"].to_list(), self.formatted_gt):
            self.assertEqual(test, gt)
        # test country
        for test, gt in zip(result["number_country"].to_list(), self.country_gt):
            self.assertEqual(test, gt)
        # test area
        for test, gt in zip(result["number_area"].to_list(), self.area_gt):
            self.assertEqual(test, gt)
        # test valid
        for test, gt in zip(result["number_valid"].to_list(), self.valid_gt):
            self.assertEqual(test, gt)
        # test possible
        for test, gt in zip(result["number_possible"].to_list(), self.possible_gt):
            self.assertEqual(test, gt)


if __name__ == "__main__":
    unittest.main()
