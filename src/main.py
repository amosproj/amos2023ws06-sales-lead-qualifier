# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

import random

from bdc import DataCollector
from database import get_database
from database.parsers import LeadParser
from evp import EstimatedValuePredictor


def run_demos():
    dc = DataCollector()
    dc.get_data_from_csv()
    print("Successfully Get Data From the CSV File")
    dc.get_data_from_api()
    print(
        "Successfully Get Data From the API and stored in JSOn file at 'src/data/collected_data.json'"
    )

    amt_leads = get_database().get_cardinality()
    lead_id = random.randint(0, amt_leads - 1)
    lead = get_database().get_lead_by_id(lead_id)

    evp = EstimatedValuePredictor()
    lead_value = evp.estimate_value(lead_id)
    print(
        f"""
        Dummy prediction for lead#{lead.lead_id}:

        Lead:
        {lead}

        This lead has a predicted probability of {lead_value.customer_probability:.2f} to become a customer.
        This lead has a predicted life time value of {lead_value.life_time_value:.2f}.

        This results in a total lead value of {lead_value.get_lead_value():.2f}.
    """
    )


if __name__ == "__main__":
    run_demos()
    dc = DataCollector()
    evp = EstimatedValuePredictor()

    amt_leads = get_database().get_cardinality()
    while True:
        lead_id = random.randint(1, amt_leads)
        try:
            choice = int(input("(1) BDC\n(2) EVP\n(3) DB\n"))
            if choice == 1:
                print("Fetching data for random lead...")
                data = dc.get_data_from_api()
                lead = LeadParser.parse_lead_from_dict(data)
                print(lead)
            if choice == 2:
                print("Predicting for random lead...")
                evp = EstimatedValuePredictor()
                lead_value = evp.estimate_value(lead_id)
                print(
                    f"""
                    Dummy prediction for lead#{lead_id}:

                    This lead has a predicted probability of {lead_value.customer_probability:.2f} to become a customer.
                    This lead has a predicted life time value of {lead_value.life_time_value:.2f}.

                    This results in a total lead value of {lead_value.get_lead_value():.2f}.
                """
                )
            if choice == 3:
                print("Displaying random lead in database...")
                lead = get_database().get_lead_by_id(lead_id)
                print(lead)
        except ValueError:
            print("Invalid choice")
