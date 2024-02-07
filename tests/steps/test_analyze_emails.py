# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 Felix Zailskas <felixzailskas@gmail.com>

import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from bdc.steps.analyze_emails import (
    AnalyzeEmails,
    analyze_email_account,
    extract_custom_domain,
)
from bdc.steps.helpers.generate_hash_leads import LeadHashGenerator
from tests import mock_hash_check


class TestExtractCustomDomain(unittest.TestCase):
    def test_valid_email(self):
        email = "user@example.com"
        result = extract_custom_domain(email)
        expected = pd.Series(["example.com", True])
        self.assertTrue(result.equals(expected))

    def test_invalid_email(self):
        email = "invalid_email"
        result = extract_custom_domain(email)
        expected = pd.Series([None, False])
        self.assertTrue(result.equals(expected))

    def test_email_with_subdomain(self):
        email = "user@sub.example.com"
        result = extract_custom_domain(email)
        expected = pd.Series(["sub.example.com", True])
        self.assertTrue(result.equals(expected))

    def test_empty_email(self):
        email = ""
        result = extract_custom_domain(email)
        expected = pd.Series([None, False])
        self.assertTrue(result.equals(expected))


class TestAnalyzeEmailAccount(unittest.TestCase):
    def _init_lead(self, Email: str, email_valid: bool):
        lead = {
            "First Name": "John",
            "Last Name": "Doe",
            "Email": Email,
            "email_valid": email_valid,
        }
        return lead

    def test_valid_email_account(self):
        lead = self._init_lead(Email="john.doe@example.com", email_valid=True)
        result = analyze_email_account(lead)
        expected = pd.Series([True, True])
        self.assertTrue(result.equals(expected))

    def test_invalid_email_account(self):
        lead = self._init_lead(Email="invalid_email", email_valid=False)
        result = analyze_email_account(lead)
        expected = pd.Series([False, False])
        self.assertTrue(result.equals(expected))

    def test_missing_first_name(self):
        lead = self._init_lead(Email="john@example.com", email_valid=True)
        result = analyze_email_account(lead)
        expected = pd.Series([True, False])
        self.assertTrue(result.equals(expected))

    def test_missing_last_name(self):
        lead = self._init_lead(Email="doe123@example.com", email_valid=True)
        result = analyze_email_account(lead)
        expected = pd.Series([False, True])
        self.assertTrue(result.equals(expected))

    def test_missing_names(self):
        lead = self._init_lead(Email="user@example.com", email_valid=True)
        lead = {"Email": "user@example.com", "email_valid": True}
        result = analyze_email_account(lead)
        expected = pd.Series([False, False])
        self.assertTrue(result.equals(expected))


class TestStepExecution(unittest.TestCase):
    step: AnalyzeEmails

    def setUp(self):
        lead_data = {
            "First Name": ["John"] * 3,
            "Last Name": ["Doe"] * 3,
            "Email": [
                "john.doe@john.com",
                "invalid_email",
                "john@yahoo.com",
            ],
        }
        self.step = AnalyzeEmails(force_refresh=True)
        self.step.df = pd.DataFrame(lead_data)

    @patch.object(LeadHashGenerator, "hash_check", mock_hash_check)
    def test_run_method(self):
        result = self.step.run()
        assert type(result) is pd.DataFrame
        columns = result.columns.to_list()
        assert all(
            col in columns
            for col in [
                "First Name",
                "Last Name",
                "Email",
                "domain",
                "email_valid",
                "first_name_in_account",
                "last_name_in_account",
            ]
        )
        assert result["domain"].to_list() == ["john.com", None, None]


if __name__ == "__main__":
    unittest.main()
