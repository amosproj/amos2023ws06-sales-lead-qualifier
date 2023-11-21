# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lucca Baumgärtner <lucca.baumgaertner@fau.de>
# SPDX-FileCopyrightText: 2023 Sophie Heasman <sophieheasmann@gmail.com>
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>
# SPDX-FileCopyrightText: 2023 Fabian-Paul Utech  <f.utech@gmx.net>
# SPDX-FileCopyrightText: 2023 Ruchita Nathani <Ruchita.nathani@fau.de>
# SPDX-FileCopyrightText: 2023 Ahmed Sheta <ahmed.sheta@fau.de>

from bdc import DataCollector
from bdc.pipeline import Pipeline
from bdc.steps import (
    EnrichCustomDomains,
    GooglePlaces,
    GPTExtractor,
    PreprocessPhonenumbers,
    ScrapeAddress,
)
from database import get_database
from evp import EstimatedValuePredictor


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
    amt_leads = get_database().get_cardinality()
    try:
        lead_id = int(
            input(f"Chose a lead_id in range [1, {amt_leads}] to predict for it\n")
        )
    except ValueError:
        print("Invalid Choice")
        return

    if lead_id < 1 or lead_id > amt_leads:
        print("Invalid Choice")
        return

    lead = get_database().get_lead_by_id(lead_id)

    evp = EstimatedValuePredictor()
    lead_value = evp.estimate_value(lead_id)
    print(
        f"""
        Dummy prediction for lead#{lead.lead_id}:

        This lead has a predicted probability of {lead_value.customer_probability:.2f} to become a customer.
        This lead has a predicted life time value of {lead_value.life_time_value:.2f}.

        This results in a total lead value of {lead_value.get_lead_value():.2f}.
    """
    )


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
    input_location = "./data/sumup_leads_email.csv"
    output_location = "./data/leads_enriched.csv"
    try:
        choice = str(input(f"Run Scrape Address step? (will take a long time) (y/N)\n"))
        if choice == "y" or choice == "Y":
            steps.append(ScrapeAddress())
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

    try:
        choice = str(
            input(
                f"Run GPT Extractor openAI API? (will use token and generate cost!) (y/N)\n"
            )
        )
        if choice == "y" or choice == "Y":
            steps.append(GPTExtractor())
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
