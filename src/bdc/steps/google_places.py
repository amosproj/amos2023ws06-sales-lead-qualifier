# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lucca Baumgärtner <lucca.baumgaertner@fau.de>
# SPDX-FileCopyrightText: 2023 Sophie Heasman <sophieheasmann@gmail.com>
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>
# SPDX-FileCopyrightText: 2023 Fabian-Paul Utech  <f.utech@gmx.net>
# SPDX-FileCopyrightText: 2023 Ruchita Nathani <Ruchita.nathani@fau.de>
# SPDX-FileCopyrightText: 2023 Ahmed Sheta <ahmed.sheta@fau.de>

from http import HTTPStatus

import googlemaps
import pandas as pd
from requests import RequestException
from tqdm import tqdm

from bdc.steps.step import Step, StepError
from config import GOOGLE_PLACES_API_KEY


class GooglePlaces(Step):
    name = "Google_Places"
    URL = "https://maps.googleapis.com/maps/api/place/textsearch/json?query="
    fields = ["business_status", "formatted_address", "name", "user_ratings_total"]
    gmaps = None

    def load_data(self) -> None:
        # don't perform this in class body or else it will fail in tests due to missing API key
        if GOOGLE_PLACES_API_KEY is None:
            raise StepError("An API key for Google Places is needed to run this step!")
        self.gmaps = googlemaps.Client(key=GOOGLE_PLACES_API_KEY)

    def verify(self) -> bool:
        return (
            self.df is not None
            and "Email" in self.df
            and "domain" in self.df
            and GOOGLE_PLACES_API_KEY is not None
        )

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
            response = self.gmaps.find_place(domain, "textquery", fields=self.fields)
            # Retrieve response
            # response = requests.get(self.URL + domain + "&key=" + GOOGLE_PLACES_API_KEY)
        except RequestException as e:
            self.log(f"Error: {str(e)}")
            return error_return_value

        if not response["status"] == HTTPStatus.OK.name:
            self.log(f"Failed to fetch data. Status code: {response['status']}")
            return error_return_value

        if "candidates" not in response or len(response["candidates"]) == 0:
            return error_return_value

        # Only look at the top result TODO: Check if we can cross check available values to rate results
        top_result = response["candidates"][0]

        results_list = [
            top_result[field] if field in top_result else None for field in self.fields
        ]

        return pd.Series(results_list)
