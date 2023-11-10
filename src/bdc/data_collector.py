# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Ruchita Nathani <ruchita.nathani@fau.de>

import csv
import json
import os
import re
import random
import requests

from database.models import ProductOfInterest


class DataCollector:
    # Limit API calls for testing
    API_LIMIT = 10

    def __init__(self):
        self.data = []

    def get_data_from_csv(self):
        """Retrieve information from the CSV file and utilize it in the Google API"""
        self.data = []
        file_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "../data/sumup_leads_email.csv"
        )
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

        return self.data

    def get_data_from_api(self):
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
                "../data/collected_data.json",
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
                        "annual_income": random.randint(0, 1000000),
                        "life_time_value": random.randint(0, 5000000),
                        "customer_probability": random.random(),
                        "product_of_interest": random.choice(list(ProductOfInterest)),
                    }

                    user_data.append(data_dict)

                json.dump(user_data, json_file, indent=4)
            return random.choice(user_data)
        else:
            return f"Failed to fetch data. Status code: {response.status_code}"

    def get_data_from_google_api(self):
        """Test of the Google Places Text Sesrch API using Ruchita's BDC skeleton"""
        # This is to show how the Google API can be used with the provided data.
        # There is no defensive programming/data preprocessing. It's a proof of concept.

        # Retrieve API key from env file
        api_file = open(
            os.path.join(
                os.path.abspath(os.path.dirname(__file__)), "../data/api_key.env"
            )
        )
        api_key = api_file.read()
        api_file.close()

        # Store all results
        user_data = []

        # Keep track of API calls
        calls = 0

        # Open json file
        file_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "../data/collected_data_google.json",
        )
        json_file = open(file_path, "w")

        # Define a regular expression pattern to match the domain part of the email
        pattern = r"@(.+)"
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json?query="

        ## Cycle through provided emails, and input domain into text search ##
        for leads in self.data:
            # Limiting API calls for testing
            if calls >= self.API_LIMIT:
                break

            # Go through each email address entry and remove the domain name (can do this in preprocessing, this is for test)
            match = re.search(pattern, leads["email_address"])
            domain = match.group(1)

            # Retrieve response
            response = requests.get(url + domain + "&key=" + api_key)

            if response.status_code == 200:
                data = response.json()

                # Only look at the top result
                top_result = data["results"][0]

                data_dict = {
                    "business_status": top_result["business_status"],
                    "company_address": top_result["formatted_address"],
                    "company_coordinates": top_result["geometry"]["location"],
                    "company_name": top_result["name"],
                    "ratings_no": top_result["user_ratings_total"],
                }

                user_data.append(data_dict)

            else:
                return f"Failed to fetch data. Status code: {response.status_code}"

            # Increment API calls
            calls += 1

        # Dump data and close
        json.dump(user_data, json_file, indent=4)
        json_file.close()
