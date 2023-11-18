# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lucca Baumgärtner <lucca.baumgaertner@fau.de>
# SPDX-FileCopyrightText: 2023 Sophie Heasman <sophieheasmann@gmail.com>
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>
# SPDX-FileCopyrightText: 2023 Fabian-Paul Utech  <f.utech@gmx.net>
# SPDX-FileCopyrightText: 2023 Ruchita Nathani <Ruchita.nathani@fau.de>
# SPDX-FileCopyrightText: 2023 Ahmed Sheta <ahmed.sheta@fau.de>

import re
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

    # fields that are expected as an output of the df.apply lambda function
    df_fields = [
        "business_status",
        "formatted_address",
        "name",
        "user_ratings_total",
        "no_candidates",
    ]
    # fields that are accessed directly from the api
    api_fields = ["business_status", "formatted_address", "name", "user_ratings_total"]

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
            and "first_name_in_account" in self.df
            and "last_name_in_account" in self.df
            and GOOGLE_PLACES_API_KEY is not None
        )

    def run(self) -> pd.DataFrame:
        tqdm.pandas(desc="Getting info from Places API")
        self.df[
            [f"{self.name.lower()}_{field}" for field in self.df_fields]
        ] = self.df.progress_apply(
            lambda lead: self.get_data_from_google_api(lead), axis=1
        )
        return self.df

    def finish(self) -> None:
        pass

    def get_data_from_google_api(self, lead_row):
        """Request Google Places Text Search API"""
        error_return_value = pd.Series([None] * len(self.df_fields))

        search_query = lead_row["domain"]

        if search_query is None and lead_row["email_valid"]:
            account_name = lead_row["Email"].split("@")[0]
            if not (
                lead_row["first_name_in_account"] and lead_row["last_name_in_account"]
            ):
                # use account name as search query and replace special characters with whitespace
                search_query = re.sub(r"[^a-zA-Z0-9\n.]", " ", account_name)
        else:
            # if account name consists only of first and last name, skip the search as no results are expected
            return error_return_value

        try:
            response = self.gmaps.find_place(
                search_query, "textquery", fields=self.api_fields
            )
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

        no_candidates = len(response["candidates"])

        results_list = [
            top_result[field] if field in top_result else None
            for field in self.api_fields
        ]

        # add number of candidates, which is not a direct field in the api response but can be derived from it
        results_list.append(no_candidates)

        return pd.Series(results_list)
