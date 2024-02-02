# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Berkay Bozkurt <resitberkaybozkurt@gmail.com>

import json
import os

from logger import get_logger

log = get_logger()

from bdc.steps import (
    AnalyzeEmails,
    GooglePlaces,
    GooglePlacesDetailed,
    GPTReviewSentimentAnalyzer,
    GPTSummarizer,
    HashGenerator,
    PreprocessPhonenumbers,
    RegionalAtlas,
    ScrapeAddress,
    SearchOffeneRegister,
    SmartReviewInsightsEnhancer,
)

DEFAULT_PIPELINE_PATH = os.path.join(os.path.dirname(__file__), "pipeline_configs/")

STEP_STR_TO_CLASS = {
    "HashGenerator": HashGenerator,
    "AnalyzeEmails": AnalyzeEmails,
    "GooglePlaces": GooglePlaces,
    "GooglePlacesDetailed": GooglePlacesDetailed,
    "GPTReviewSentimentAnalyzer": GPTReviewSentimentAnalyzer,
    "GPTSummarizer": GPTSummarizer,
    "PreprocessPhonenumbers": PreprocessPhonenumbers,
    "RegionalAtlas": RegionalAtlas,
    "ScrapeAddress": ScrapeAddress,
    "SearchOffeneRegister": SearchOffeneRegister,
    "SmartReviewInsightsEnhancer": SmartReviewInsightsEnhancer,
}

# Please do not write following lists! Use the functions below instead.
_additional_pipeline_steps = [
    (ScrapeAddress, "Scrape Address", "(will take a long time)"),
    (SearchOffeneRegister, "Search OffeneRegister", "(will take a long time)"),
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
]

_initial_pipeline_steps = [
    (HashGenerator, "Hash Generator", ""),
    (AnalyzeEmails, "Analyze Emails", ""),
]
# Please do not write above lists! Use the functions below instead.


def get_pipeline_steps() -> list:
    """
    Returns a copy of the pipeline steps, which includes both the initial pipeline steps
    and the additional pipeline steps.

    Returns:
        list: A copy of the pipeline steps.
    """
    return (_initial_pipeline_steps + _additional_pipeline_steps).copy()


def get_pipeline_initial_steps() -> list:
    """
    Returns a copy of the initial pipeline steps.

    Returns:
        list: A copy of the initial pipeline steps.
    """
    return _initial_pipeline_steps.copy()


def get_pipeline_additional_steps() -> list:
    """
    Returns a copy of the additional pipeline steps.

    Returns:
        list: A copy of the additional pipeline steps.
    """
    return _additional_pipeline_steps.copy()


def get_all_available_pipeline_json_configs(
    config_path: str = DEFAULT_PIPELINE_PATH,
) -> list:
    """
    Returns a list of all available pipeline json configs in the given path.
    :param config_path: Path to the pipeline json configs
    :return: List of all available pipeline json configs
    """
    return [f for f in os.listdir(config_path) if f.endswith(".json")]


def get_pipeline_config_from_json(
    config_name: str, config_path: str = DEFAULT_PIPELINE_PATH
) -> list:
    """
    Retrieves the pipeline configuration from a JSON file.

    Args:
        config_name (str): The name of the configuration file.
        config_path (str, optional): The path to the configuration file. Defaults to DEFAULT_PIPELINE_PATH.

    Returns:
        list: A list of pipeline steps.

    """
    with open(os.path.join(config_path, config_name), "r") as f:
        steps_json = json.load(f)
        steps = []
        for step in steps_json["config"]["steps"]:
            log.info(f"Adding step {step}")
            steps.append(
                (STEP_STR_TO_CLASS[step["name"]](force_refresh=step["force_refresh"]))
            )

        return steps
