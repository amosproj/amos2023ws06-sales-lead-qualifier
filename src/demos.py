# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lucca Baumgärtner <lucca.baumgaertner@fau.de>
# SPDX-FileCopyrightText: 2023 Sophie Heasman <sophieheasmann@gmail.com>
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>
# SPDX-FileCopyrightText: 2023 Fabian-Paul Utech  <f.utech@gmx.net>
# SPDX-FileCopyrightText: 2023 Ruchita Nathani <Ruchita.nathani@fau.de>
# SPDX-FileCopyrightText: 2023 Ahmed Sheta <ahmed.sheta@fau.de>

import pandas as pd
from sklearn.metrics import mean_squared_error

from bdc import DataCollector
from bdc.pipeline import Pipeline
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
from database import get_database
from database.parsers import LeadParser
from evp import EstimatedValuePredictor
from evp.data_processing import split_dataset
from evp.predictors import Predictors
from logger import get_logger
from preprocessing import Preprocessing

log = get_logger()

# Constants and configurations
LEADS_TRAIN_FILE = "data/leads_train.csv"
LEADS_TEST_FILE = "data/leads_test.csv"
INPUT_FILE_BDC = "../data/sumup_leads_email.csv"
OUTPUT_FILE_BDC = "../data/collected_data.json"


# Utility Functions
def get_yes_no_input(prompt: str) -> bool:
    while True:
        user_input = input(prompt).strip().lower()
        if user_input in ["y", "yes"]:
            return True
        elif user_input in ["n", "no"]:
            return False
        else:
            print("Invalid input. Please enter (yes/no) or (y/N).")


def get_int_input(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a valid integer.")


# bdc_demo
def bdc_demo():
    dc = DataCollector()
    try:
        choice = get_int_input("(1) Read CSV\n(2) Dummy API\n")
        if choice == 1:
            dc.get_data_from_csv(file_path=INPUT_FILE_BDC)
        elif choice == 2:
            dc.get_data_from_api(file_path=OUTPUT_FILE_BDC)
        else:
            print("Invalid choice")
    except ValueError:
        print("Invalid choice")


# evp demo
def evp_demo():
    evp = EstimatedValuePredictor(
        model_type=Predictors.LinearRegression,
        model_path=input("Provide model path\n")
        if get_yes_no_input("Load model from file? (y/N)\n")
        else None,
    )

    if get_yes_no_input("Split dataset (y/N)\n"):
        split_dataset(
            "data/leads_enriched.csv",
            "data/leads",
            0.8,
            0.1,
            0.1,
            add_labels=get_yes_no_input("Add dummy labels (the lead value) (y/N)\n"),
        )

    while True:
        choice = get_int_input(
            "(1) Train\n(2) Test\n(3) Predict on single lead\n(4) Save model\n(5) Exit\n"
        )
        if choice == 1:
            evp.train(LEADS_TRAIN_FILE)
        elif choice == 2:
            test_evp_model(evp)
        elif choice == 3:
            predict_single_lead(evp)
        elif choice == 4:
            evp.save_models(input("Provide model path\n"))
        elif choice == 5:
            break
        else:
            print("Invalid choice")


def test_evp_model(evp: EstimatedValuePredictor):
    leads = LeadParser.parse_leads_from_csv(LEADS_TEST_FILE)
    predictions = [evp.estimate_value(lead) for lead in leads]
    true_labels = [lead.lead_value for lead in leads]
    print(
        f"EVP has a mean squared error of {mean_squared_error(true_labels, predictions)} on the test set."
    )


def predict_single_lead(evp: EstimatedValuePredictor):
    leads = LeadParser.parse_leads_from_csv(LEADS_TEST_FILE)
    lead_id = get_int_input(f"Choose a lead_id in range [0, {len(leads) - 1}]\n")
    if 0 <= lead_id < len(leads):
        prediction = evp.estimate_value(leads[lead_id])
        print(
            f"Lead has predicted value of {prediction} and true value of {leads[lead_id].lead_value}"
        )
    else:
        print("Invalid Choice")


# db_demo
def db_demo():
    amt_leads = get_database().get_cardinality()
    lead_id = get_int_input(f"Choose a lead_id in range [1, {amt_leads}]\n")
    if 1 <= lead_id <= amt_leads:
        print(get_database().get_lead_by_id(lead_id))
    else:
        print("Invalid Choice")


def add_step_if_requested(
    steps, step_classes, step_desc, step_warning_message: str = ""
):
    if get_yes_no_input(f"Run {step_desc} {step_warning_message}(y/N)?\n"):
        force = get_yes_no_input("Force execution if data is present? (y/N)\n")
        for cls in step_classes:
            steps.append(cls(force_refresh=force))


# pipeline_demo
def pipeline_demo():
    steps = [AnalyzeEmails(force_refresh=True)]
    additional_steps = [
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

    if get_yes_no_input(f"Run Demo pipeline with all steps (y/N)?\n"):
        for step_classes, _, _ in additional_steps:
            step_instances = [cls(force_refresh=True) for cls in step_classes]
            steps.extend(step_instances)
    else:
        for step_classes, desc, warning_message in additional_steps:
            add_step_if_requested(steps, step_classes, desc, warning_message)

    limit = get_int_input("Set limit for data points to be processed (0=No limit)\n")
    limit = limit if limit > 0 else None

    if (
        limit is not None
        and get_database().DF_OUTPUT == "s3://amos--data--events/leads/enriched.csv"
    ):
        if get_yes_no_input(
            f"The output cannot be limited when uploading to {get_database().DF_OUTPUT}.\nThe limit will be removed, and the pipeline will be executed on the full database.\n\nWould you like to continue? (y/n)\n"
        ):
            limit = None
        else:
            return

    steps_info = "\n".join([str(step) for step in steps])
    log.info(
        f"Running Pipeline with steps:\n{steps_info}\ninput_location={get_database().get_input_path()}\noutput_location={get_database().get_output_path()}"
    )

    pipeline = Pipeline(
        steps=steps,
        limit=limit,
    )

    pipeline.run()


def preprocessing_demo():
    if get_yes_no_input("Filter out the API-irrelevant data? (y/n)"):
        preprocessor = Preprocessing(filter_null_data=True)
    else:
        preprocessor = Preprocessing(filter_null_data=False)
    df = preprocessor.implement_preprocessing_pipeline()
    preprocessor.save_preprocessed_data()
