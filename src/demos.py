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
from bdc.steps import (
    EnrichCustomDomains,
    GooglePlaces,
    PreprocessPhonenumbers,
    ScrapeAddress,
)
from database import get_database
from database.parsers import LeadParser
from evp import EstimatedValuePredictor
from evp.data_processing import split_dataset
from evp.predictors import Predictors


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
    print(f"Creating EVP from model {model_path}")
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
            "data/save_leads_enriched.csv",
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
    steps = [EnrichCustomDomains()]
    input_location = "data/sumup_leads_email.csv"
    output_location = "data/leads_enriched.csv"
    try:
        choice = str(input(f"Run Scrape Address step? (will take a long time) (y/N)\n"))
        if choice == "y" or choice == "Y":
            steps.append(ScrapeAddress())
    except ValueError:
        print("Invalid Choice")

    try:
        choice = str(input(f"Run Facebook Graph API step? (will use token) (y/N)\n"))
        if choice == "y" or choice == "Y":
            steps.append(FacebookGraphAPI())
    except ValueError:
        print("Invalid Choice")

    try:
        choice = str(
            input(
                f"Validate the phone number and using the phone number to get information about the location? (y/N)\n"
            )
        )
        if choice == "y" or choice == "Y":
            steps.append(PreprocessPhonenumbers())
    except ValueError:
        print("Invalid Choice")

    try:
        choice = str(
            input(f"Run Google API step? (will use token and generate cost!) (y/N)\n")
        )
        if choice == "y" or choice == "Y":
            steps.append(GooglePlaces())
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

    print(f"Running Pipeline with {steps=}, {input_location=}, {output_location=}")
    pipeline = Pipeline(
        steps=steps,
        input_location=input_location,
        output_location=output_location,
        limit=limit,
    )
    pipeline.run()
