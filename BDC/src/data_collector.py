# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Ruchita Nathani <ruchita.nathani@fau.de>
import csv
import requests
import json
import os


class DataCollector:
    def __init__(self):
        self.data = []

    @staticmethod
    def get_data_from_csv():
        """Retrieve information from the CSV file and utilize it in the Google API"""
        data = []
        file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../data/given_data.csv')
        with open(file_path, 'r', encoding='utf8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)

            for row in csv_reader:
                data_dict = {
                    "last_name": row[0],
                    "first_name": row[1],
                    "company_account": row[2],
                    "phone": row[3],
                    "email": row[4],
                }

                data.append(data_dict)
        # self.data = data
        return data

    @staticmethod
    def get_data_from_api():
        """will utilize the data from the CSV file in the API key we are using, retrieve the necessary information from the API, and extract specific information that we need for the predictor. This relevant data will be stored in a JSON file."""
        api_url = "https://dummyjson.com/users"

        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../data/collected_data.json')
            with open(file_path, "w") as json_file:
                user_data = []
                for users in data["users"]:
                    data_dict = {
                        "user_id": users["id"],
                        "first_name": users["firstName"],
                        "last_name": users["lastName"],
                        "phone": users["phone"],
                        "email": users["email"],
                        "company_address": users["company"]["address"]["address"],
                        "company_department": users["company"]["department"],
                        "company_name": users["company"]["name"],
                    }

                    user_data.append(data_dict)

                json.dump(user_data, json_file, indent=4)
            return
        else:
            return f"Failed to fetch data. Status code: {response.status_code}"
