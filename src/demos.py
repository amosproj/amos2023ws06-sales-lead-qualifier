# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lucca Baumgärtner <lucca.baumgaertner@fau.de>
# SPDX-FileCopyrightText: 2023 Sophie Heasman <sophieheasmann@gmail.com>
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>
# SPDX-FileCopyrightText: 2023 Fabian-Paul Utech  <f.utech@gmx.net>
# SPDX-FileCopyrightText: 2023 Ruchita Nathani <Ruchita.nathani@fau.de>
# SPDX-FileCopyrightText: 2023 Ahmed Sheta <ahmed.sheta@fau.de>

import numpy as np
from sklearn.metrics import mean_squared_error

from bdc import DataCollector
from bdc.pipeline import Pipeline
from bdc.pipeline_dal import PipelineDAL
from bdc.steps import (
    AnalyzeEmails,
    FacebookGraphAPI,
    GooglePlaces,
    GooglePlacesDetailed,
    GPTReviewSentimentAnalyzer,
    PreprocessPhonenumbers,
    RegionalAtlas,
    ScrapeAddress,
)
from bdc.steps.step import Step
from database import get_database
from database.parsers import LeadParser
from evp import EstimatedValuePredictor
from evp.data_processing import split_dataset
from evp.predictors import Predictors
from logger import get_logger

log = get_logger()

S3_BUCKET = "amos--data--events"


def bdc_demo():
    dc = DataCollector()
    input_file = "../data/sumup_leads_email.csv"
    output_file = "../data/collected_data.json"
    try:
        choice = int(input("(1) read CSV\n(2) Dummy API\n"))
        match choice:
            case 1:
                dc.get_data_from_csv(file_path=input_file)
            case 2:
                dc.get_data_from_api(file_path=output_file)
            case other:
                print("Invalid choice")
    except ValueError:
        print("Invalid choice")


def evp_demo():
    choice = str(input("Load model from file? (y/N)\n"))
    if choice == "y" or choice == "Y":
        model_path = str(input("Provide model path\n"))
    else:
        model_path = None
    log.info(f"Creating EVP from model {model_path}")
    evp = EstimatedValuePredictor(
        model_type=Predictors.LinearRegression, model_path=model_path
    )
    choice = str(input("Split dataset (y/N)\n"))
    if choice == "y" or choice == "Y":
        choice = str(input("Add dummy labels (the lead value) (y/N)\n"))
        add_labels = False
        if choice == "y" or choice == "Y":
            add_labels = True
        split_dataset(
            "data/leads_enriched.csv",
            "data/leads",
            0.8,
            0.1,
            0.1,
            add_labels=add_labels,
        )
    while True:
        try:
            choice = int(
                input(
                    "(1) Train\n(2) Test\n(3) Predict on single lead\n(4) Save model\n(5) Exit\n"
                )
            )
            match choice:
                case 1:
                    evp.train("data/leads_train.csv")
                case 2:
                    leads = LeadParser.parse_leads_from_csv("data/leads_test.csv")
                    predictions = np.array([evp.estimate_value(lead) for lead in leads])
                    true_labels = np.array([lead.lead_value for lead in leads])
                    mean_sq_error = mean_squared_error(true_labels, predictions)
                    print(
                        f"EVP has a mean squared error of {mean_sq_error} on the test set."
                    )
                case 3:
                    leads = LeadParser.parse_leads_from_csv("data/leads_test.csv")
                    try:
                        lead_id = int(
                            input(
                                f"Chose a lead_id in range [0, {len(leads) - 1}] to predict for it\n"
                            )
                        )
                        if lead_id < 0 or lead_id > len(leads) - 1:
                            print("Invalid Choice")
                            continue
                    except ValueError:
                        print("Invalid Choice")
                        continue
                    prediction = evp.estimate_value(leads[lead_id])
                    print(
                        f"Lead has predicted value of {prediction} and true value of {leads[lead_id].lead_value}"
                    )
                case 4:
                    model_path = str(input("Provide model path\n"))
                    evp.save_models(model_path)
                case 5:
                    break
        except ValueError:
            print("Invalid choice")


def db_demo():
    amt_leads = get_database().get_cardinality()
    try:
        lead_id = int(
            input(f"Chose a lead_id in range [1, {amt_leads}] to show its DB entry\n")
        )
    except ValueError:
        print("Invalid Choice")
        return
    if lead_id < 1 or lead_id > amt_leads:
        print("Invalid Choice")
        return
    lead = get_database().get_lead_by_id(lead_id)
    print(lead)


def pipeline_demo():
    steps: list[Step] = [AnalyzeEmails(force_refresh=True)]
    input_location = f"s3://{S3_BUCKET}/leads/enriched.csv"

    index_col = None
    output_location_local = "./data/leads_enriched.csv"
    output_location_remote = None

    # data is saved locally, unless the limit is None and the user decides to store
    # the data in a remote database
    db = "local"

    try:
        choice = str(input(f"Run Scrape Address step? (will take a long time) (y/N)\n"))
        if choice == "y" or choice == "Y":
            choice = str(
                input(f"Do you want to force execution if the data is present? (y/N)\n")
            )
            force_execution = choice == "y" or choice == "Y"
            steps.append(ScrapeAddress(force_refresh=force_execution))
    except ValueError:
        print("Invalid Choice")

    try:
        choice = str(input(f"Run Facebook Graph API step? (will use token) (y/N)\n"))
        if choice == "y" or choice == "Y":
            choice = str(
                input(f"Do you want to force execution if the data is present? (y/N)\n")
            )
            force_execution = choice == "y" or choice == "Y"
            steps.append(FacebookGraphAPI(force_refresh=force_execution))
    except ValueError:
        print("Invalid Choice")

    try:
        choice = str(
            input(
                f"Validate the phone number and using the phone number to get information about the location? (y/N)\n"
            )
        )
        if choice == "y" or choice == "Y":
            choice = str(
                input(f"Do you want to force execution if the data is present? (y/N)\n")
            )
            force_execution = choice == "y" or choice == "Y"
            steps.append(PreprocessPhonenumbers(force_refresh=force_execution))
    except ValueError:
        print("Invalid Choice")

    try:
        choice = str(
            input(f"Run Google API step? (will use token and generate cost!) (y/N)\n")
        )
        if choice == "y" or choice == "Y":
            choice = str(
                input(f"Do you want to force execution if the data is present? (y/N)\n")
            )
            force_execution = choice == "y" or choice == "Y"
            steps.append(GooglePlaces(force_refresh=force_execution))
            steps.append(GooglePlacesDetailed(force_refresh=force_execution))
    except ValueError:
        print("Invalid Choice")

    try:
        choice = str(
            input(
                f"Run open API Sentiment Analyzer ? (will use token and generate cost!) (y/N)\n"
            )
        )
        if choice == "y" or choice == "Y":
            choice = str(
                input(f"Do you want to force execution if the data is present? (y/N)\n")
            )
            force_execution = choice == "y" or choice == "Y"
            steps.append(GPTReviewSentimentAnalyzer(force_refresh=force_execution))
    except ValueError:
        print("Invalid Choice")

    try:
        choice = str(input(f"Use the Regionalatlas? (y/N)\n"))
        if choice == "y" or choice == "Y":
            steps.append(RegionalAtlas(force_refresh=True))
    except ValueError:
        print("Invalid Choice")

    limit = None

    try:
        choice = int(input(f"Set limit for data point to be processed\n"))
        if choice > 0:
            limit = choice
        else:
            print("Invalid Choice, no limit set")
    except ValueError:
        print("Invalid Choice, no limit set")

    if limit is None:
        try:
            choice = str(
                input(
                    f"Do you want to save the output data to S3? Will replace the current file!\n"
                )
            )
            if choice == "y" or choice == "Y":
                output_location_remote = f"s3://{S3_BUCKET}/leads/enriched.csv"
                db = "S3"
        except ValueError:
            print("Invalid Choice")

    log.info(
        f"Running Pipeline with {steps=}, {input_location=}, {output_location_local=}, {output_location_remote=}"
    )

    choice = input("Do you want to run the Pipeline with the DAL? (y/n)\n")

    if choice == "y" or choice == "Y":
        pipeline = PipelineDAL(
            steps=steps,
            db=db,
            limit=limit,
        )
        pipeline.run()
    else:
        pipeline = Pipeline(
            steps=steps,
            input_location=input_location,
            output_location_local=output_location_local,
            output_location_remote=output_location_remote,
            limit=limit,
            index_col=index_col,
        )
        pipeline.run()
