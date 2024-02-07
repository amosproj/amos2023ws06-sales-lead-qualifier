# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 Felix Zailskas <felixzailskas@gmail.com>

import unittest
from unittest.mock import MagicMock, mock_open, patch

from bdc.steps import *
from demo.pipeline_utils import (
    get_all_available_pipeline_json_configs,
    get_pipeline_additional_steps,
    get_pipeline_config_from_json,
    get_pipeline_initial_steps,
    get_pipeline_steps,
)


class TestPipelineUtils(unittest.TestCase):
    def test_get_pipeline_steps(self):
        steps = get_pipeline_steps()
        self.assertEqual(
            [
                (HashGenerator, "Hash Generator", ""),
                (AnalyzeEmails, "Analyze Emails", ""),
                (
                    SearchOffeneRegister,
                    "Search OffeneRegister",
                    "(will take a long time)",
                ),
                (PreprocessPhonenumbers, "Phone Number Validation", ""),
                (
                    GooglePlaces,
                    "Google API",
                    "(will use token and generate cost!)",
                ),
                (
                    GooglePlacesDetailed,
                    "Google API Detailed",
                    "(will use token and generate cost!)",
                ),
                (
                    GPTReviewSentimentAnalyzer,
                    "openAI GPT Sentiment Analyzer",
                    "(will use token and generate cost!)",
                ),
                (
                    GPTSummarizer,
                    "openAI GPT Summarizer",
                    "(will use token and generate cost!)",
                ),
                (
                    SmartReviewInsightsEnhancer,
                    "Smart Review Insights",
                    "(will take looong time!)",
                ),
                (RegionalAtlas, "Regionalatlas", ""),
            ],
            steps,
        )

    def test_get_pipeline_initial_steps(self):
        initial_steps = get_pipeline_initial_steps()
        self.assertEqual(
            [
                (HashGenerator, "Hash Generator", ""),
                (AnalyzeEmails, "Analyze Emails", ""),
            ],
            initial_steps,
        )

    def test_get_pipeline_additional_steps(self):
        additional_steps = get_pipeline_additional_steps()
        self.assertEqual(
            [
                (
                    SearchOffeneRegister,
                    "Search OffeneRegister",
                    "(will take a long time)",
                ),
                (PreprocessPhonenumbers, "Phone Number Validation", ""),
                (
                    GooglePlaces,
                    "Google API",
                    "(will use token and generate cost!)",
                ),
                (
                    GooglePlacesDetailed,
                    "Google API Detailed",
                    "(will use token and generate cost!)",
                ),
                (
                    GPTReviewSentimentAnalyzer,
                    "openAI GPT Sentiment Analyzer",
                    "(will use token and generate cost!)",
                ),
                (
                    GPTSummarizer,
                    "openAI GPT Summarizer",
                    "(will use token and generate cost!)",
                ),
                (
                    SmartReviewInsightsEnhancer,
                    "Smart Review Insights",
                    "(will take looong time!)",
                ),
                (RegionalAtlas, "Regionalatlas", ""),
            ],
            additional_steps,
        )

    def test_get_all_available_pipeline_json_configs(self):
        # Create a temporary directory and add some JSON files for testing
        with patch(
            "os.listdir", MagicMock(return_value=["config1.json", "config2.json"])
        ):
            configs = get_all_available_pipeline_json_configs(config_path="fake_path")
            self.assertEqual(configs, ["config1.json", "config2.json"])

    def test_get_pipeline_config_from_json(self):
        # Create a temporary JSON file for testing
        mock_json_content = """
            {
                "config": {
                    "steps": [
                        {"name": "HashGenerator", "force_refresh": true},
                        {"name": "AnalyzeEmails", "force_refresh": false},
                        {"name": "GooglePlacesDetailed", "force_refresh": false},
                        {"name": "SearchOffeneRegister", "force_refresh": true}
                    ]
                }
            }
        """
        steps_gt = [
            HashGenerator(force_refresh=True),
            AnalyzeEmails(force_refresh=False),
            GooglePlacesDetailed(force_refresh=False),
            SearchOffeneRegister(force_refresh=True),
        ]
        with patch("builtins.open", mock_open(read_data=mock_json_content)):
            steps = get_pipeline_config_from_json(
                "fake_config.json", config_path="fake_path"
            )
            for step, gt in zip(steps, steps_gt):
                self.assertEqual(type(step), type(gt))
                self.assertEqual(step.name, gt.name)
                self.assertEqual(step.force_refresh, gt.force_refresh)


if __name__ == "__main__":
    unittest.main()
