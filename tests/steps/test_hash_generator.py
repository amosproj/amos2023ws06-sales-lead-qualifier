# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 Felix Zailskas <felixzailskas@gmail.com>

import hashlib
import unittest

import pandas as pd

from bdc.steps.hash_generator import HashGenerator


class YourClassTests(unittest.TestCase):
    def setUp(self):
        self.lead_data = {
            "First Name": ["John"],
            "Last Name": ["Doe"],
            "Company / Account": ["ABC Corp"],
            "Phone": ["+4912345678"],
            "Email": ["john.doe@john.com"],
        }
        self.step = HashGenerator(force_refresh=True)
        self.step.df = pd.DataFrame(self.lead_data)

    def test_hash_lead(self):
        # Calculate the expected hash manually based on the data
        expected_hash = hashlib.sha256(
            ("John" + "Doe" + "ABC Corp" + "+4912345678" + "john.doe@john.com").encode()
        ).hexdigest()

        # Call the hash_lead method with the sample data
        result = self.step.run()

        # Assert that the actual hash matches the expected hash
        assert type(result) is pd.DataFrame
        columns = result.columns.to_list()
        assert all(
            col in columns
            for col in [
                "First Name",
                "Last Name",
                "Email",
                "Company / Account",
                "Phone",
                "lead_hash",
            ]
        )
        self.assertEqual(result.iloc[0]["lead_hash"], expected_hash)


if __name__ == "__main__":
    unittest.main()
