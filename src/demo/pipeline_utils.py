# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Berkay Bozkurt <resitberkaybozkurt@gmail.com>

from bdc.steps import (
    AnalyzeEmails,
    FacebookGraphAPI,
    GooglePlaces,
    GooglePlacesDetailed,
    GPTReviewSentimentAnalyzer,
    GPTSummarizer,
    PreprocessPhonenumbers,
    RegionalAtlas,
    ScrapeAddress,
    SmartReviewInsightsEnhancer,
)

# Please do not write following lists! Use the functions below instead.
_additional_pipeline_steps = [
    ([ScrapeAddress], "Scrape Address", "(will take a long time)"),
    ([FacebookGraphAPI], "Facebook Graph API", "(will use token)"),
    ([PreprocessPhonenumbers], "Phone Number Validation", ""),
    (
        [GooglePlaces, GooglePlacesDetailed],
        "Google API",
        "(will use token and generate cost!)",
    ),
    (
        [GPTReviewSentimentAnalyzer, GPTSummarizer],
        "open API Sentiment Analyzer & Summarizer",
        "(will use token and generate cost!)",
    ),
    (
        [SmartReviewInsightsEnhancer],
        "Smart Review Insights",
        "(will take looong time!)",
    ),
    ([RegionalAtlas], "Regionalatlas", ""),
]

_initial_pipeline_steps = [AnalyzeEmails(force_refresh=True)]


def get_pipeline_steps() -> list:
    return (_initial_pipeline_steps + _additional_pipeline_steps).copy()


def get_pipeline_initial_steps() -> list:
    return _initial_pipeline_steps.copy()


def get_pipeline_additional_steps() -> list:
    return _additional_pipeline_steps.copy()
