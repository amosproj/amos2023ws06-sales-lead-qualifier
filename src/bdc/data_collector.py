# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Ruchita Nathani <ruchita.nathani@fau.de>

import csv
import json
import os
import random

import requests

from database.models import AnnualIncome, ProductOfInterest


class DataCollector:
    # Limit API calls for testing
    API_LIMIT = 10

    def __init__(self):
        self.data = []

    def get_data_from_csv(self, file_path: str = "../data/sumup_leads_email.csv"):
        """Retrieve information from the CSV file and utilize it in the Google API"""
        self.data = []
        file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), file_path)
        try:
            with open(file_path, "r", encoding="utf8") as file:
                csv_reader = csv.reader(file)
                next(csv_reader)

                for row in csv_reader:
                    data_dict = {
                        "last_name": row[0],
                        "first_name": row[1],
                        "company_account": row[2],
                        "phone_number": row[3],
                        "email_address": row[4],
                    }

                    self.data.append(data_dict)
            print(f"Successfully read data from {file_path}")
        except FileNotFoundError as e:
            print(f"Error: Input file {file_path} for BDC not found.")

        return self.data

    def get_data_from_api(self, file_path: str = "../data/collected_data.json"):
        """will utilize the data from the CSV file in the API key we are using, retrieve the necessary information from the API, and extract specific information that we need for the predictor. This relevant data will be stored in a JSON file."""
        api_url = "https://dummyjson.com/users"
        try:
            response = requests.get(api_url)
        except Exception as e:
            print("Error when fetching dummies")
            return None

        if response.status_code == 200:
            data = response.json()
            file_path = os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                file_path,
            )
            with open(file_path, "w") as json_file:
                user_data = []
                for users in data["users"]:
                    data_dict = {
                        "lead_id": users["id"],
                        "first_name": users["firstName"],
                        "last_name": users["lastName"],
                        "phone_number": users["phone"],
                        "email_address": users["email"],
                        "company_address": users["company"]["address"]["address"],
                        "company_department": users["company"]["department"],
                        "company_name": users["company"]["name"],
                        "annual_income": random.randint(0, AnnualIncome.Class10.value),
                        "life_time_value": random.randint(
                            0, AnnualIncome.Class10.value
                        ),
                        "customer_probability": random.random(),
                        "product_of_interest": random.choice(list(ProductOfInterest)),
                    }

                    user_data.append(data_dict)

                json.dump(user_data, json_file, indent=4)
            print(f"Successfully fetched data from {api_url} and stored at {file_path}")
            return random.choice(user_data)
        else:
            print(
                f"Failed to fetch data from {api_url}. Status code: {response.status_code}"
            )
            return None
