# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lucca Baumgärtner <lucca.baumgaertner@fau.de>
# SPDX-FileCopyrightText: 2023 Sophie Heasman <sophieheasmann@gmail.com>
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>
# SPDX-FileCopyrightText: 2023 Fabian-Paul Utech  <f.utech@gmx.net>
# SPDX-FileCopyrightText: 2023 Ruchita Nathani <Ruchita.nathani@fau.de>
# SPDX-FileCopyrightText: 2023 Ahmed Sheta <ahmed.sheta@fau.de>

from http import HTTPStatus

import requests
from requests import RequestException
from tqdm import tqdm

from bdc.steps.step import Step
from config import GOOGLE_PLACES_API_KEY


class GooglePlacesStep(Step):
    name = "Google-Places"

    fields = ["business_status", "formatted_address", "name", "ratings_no"]

    def load_data(self) -> None:
        pass

    def verify(self) -> bool:
        return self.df is not None and "Email" in self.df and "domain" in self.df

    def run(self) -> None:
        tqdm.pandas(desc="Getting info from Places API")
        self.df = self.df[:100]
        values = self.df.progress_apply(
            lambda lead: self.get_data_from_google_api(lead), axis=1
        )
        self.df[self.fields] = values
        pass

    def finish(self) -> None:
        pass

    def get_data_from_google_api(self, lead_row):
        """Test of the Google Places Text Sesrch API using Ruchita's BDC skeleton"""
        # This is to show how the Google API can be used with the provided data.
        # There is no defensive programming/data preprocessing. It's a proof of concept.

        # Retrieve API key from env file

        api_key = GOOGLE_PLACES_API_KEY

        # Keep track of API calls
        calls = 0

        # Define a regular expression pattern to match the domain part of the email
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json?query="

        # Go through each email address entry and remove the domain name (can do this in preprocessing, this is for test)
        domain = lead_row["domain"]
        if domain is None:
            return [None, None, None, None]

        try:
            # Retrieve response
            response = requests.get(url + domain + "&key=" + api_key)
        except RequestException as e:
            self.log(f"Error: {str(e)}")
            return [None, None, None, None]

        if response.status_code == HTTPStatus.OK:
            data = response.json()

            # data_dict = {
            #     "business_status": top_result["business_status"],
            #    "company_address": top_result["formatted_address"],
            #    "company_coordinates": top_result["geometry"]["location"],
            #    "company_name": top_result["name"],
            #    "ratings_no": top_result["user_ratings_total"],
            # }

            if "results" in data and len(data["results"]) > 0:
                # Only look at the top result
                top_result = data["results"][0]

                business_status = (
                    top_result["business_status"]
                    if "business_satus" in top_result
                    else None
                )
                formatted_address = (
                    top_result["formatted_address"]
                    if "formatted_address" in top_result
                    else None
                )
                name = top_result["name"] if "name" in top_result else None
                ratings_no = (
                    top_result["user_ratings_total"]
                    if "user_ratings_total" in top_result
                    else None
                )

                return [business_status, formatted_address, name, ratings_no]

        else:
            self.log(f"Failed to fetch data. Status code: {response.status_code}")
            return [None, None, None, None]
