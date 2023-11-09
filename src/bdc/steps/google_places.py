# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lucca Baumgärtner <lucca.baumgaertner@fau.de>
# SPDX-FileCopyrightText: 2023 Sophie Heasman <sophieheasmann@gmail.com>
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>
# SPDX-FileCopyrightText: 2023 Fabian-Paul Utech  <f.utech@gmx.net>
# SPDX-FileCopyrightText: 2023 Ruchita Nathani <Ruchita.nathani@fau.de>
# SPDX-FileCopyrightText: 2023 Ahmed Sheta <ahmed.sheta@fau.de>

from http import HTTPStatus

import pandas as pd
import requests
from requests import RequestException
from tqdm import tqdm

from bdc.steps.step import Step
from config import GOOGLE_PLACES_API_KEY


class GooglePlacesStep(Step):
    # TODO: replace the requests package with the python client for Google Maps Service https://github.com/googlemaps/google-maps-services-python
    name = "Google_Places"
    URL = "https://maps.googleapis.com/maps/api/place/textsearch/json?query="
    fields = ["business_status", "formatted_address", "name", "user_ratings_total"]

    def load_data(self) -> None:
        pass

    def verify(self) -> bool:
        return self.df is not None and "Email" in self.df and "domain" in self.df

    def run(self) -> None:
        tqdm.pandas(desc="Getting info from Places API")
        self.df[
            [f"{self.name.lower()}_{field}" for field in self.fields]
        ] = self.df.progress_apply(
            lambda lead: self.get_data_from_google_api(lead), axis=1
        )
        return self.df

    def finish(self) -> None:
        pass

    def get_data_from_google_api(self, lead_row):
        """Request Google Places Text Search API"""
        error_return_value = pd.Series([None] * len(self.fields))

        # Go through each email address entry and remove the domain name (can do this in preprocessing, this is for test)
        domain = lead_row["domain"]
        if domain is None:
            return error_return_value

        try:
            # Retrieve response
            response = requests.get(self.URL + domain + "&key=" + GOOGLE_PLACES_API_KEY)
        except RequestException as e:
            self.log(f"Error: {str(e)}")
            return error_return_value

        if not response.status_code == HTTPStatus.OK:
            self.log(f"Failed to fetch data. Status code: {response.status_code}")
            return error_return_value

        data = response.json()

        if "results" not in data or len(data["results"]) == 0:
            return error_return_value

        # Only look at the top result TODO: Check if we can cross check available values to rate results
        top_result = data["results"][0]

        results_list = [
            top_result[field] if field in top_result else None for field in self.fields
        ]

        return pd.Series(results_list)
