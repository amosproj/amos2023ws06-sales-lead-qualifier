# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lucca Baumgärtner <lucca.baumgaertner@fau.de>
# SPDX-FileCopyrightText: 2023 Sophie Heasman <sophieheasmann@gmail.com>
# SPDX-FileCopyrightText: 2023 Ruchita Nathani <Ruchita.nathani@fau.de>
# SPDX-FileCopyrightText: 2023 Ahmed Sheta <ahmed.sheta@fau.de>

import json
import os
from http import HTTPStatus

import boto3
import googlemaps
import pandas as pd
from googlemaps.exceptions import ApiError, HTTPError, Timeout, TransportError
from requests import RequestException
from tqdm import tqdm

from bdc.steps.step import Step, StepError
from config import GOOGLE_PLACES_API_KEY
from database import get_database
from logger import get_logger

log = get_logger()


class GooglePlacesDetailed(Step):
    """
    The GooglePlacesDetailed step will try to gather detailed information for a given google business entry, identified
    by the place ID. This information could be the website link, the review text and the business type. Reviews will
    be saved to a separate location based on the persistence settings this could be local or AWS S3.

    Attributes:
        name: Name of this step, used for logging
        added_cols: List of fields that will be added to the main dataframe by executing this step
        required_cols: List of fields that are required to be existent in the input dataframe before performing this step
    """

    name = "Google_Places_Detailed"

    # fields that are expected as an output of the df.apply lambda function
    df_fields = ["website", "type"]

    # Weirdly the expression [f"{name}_{field}" for field in df_fields] gives an error as name is not in the scope of the iterator
    added_cols = [
        name + field
        for (name, field) in zip(
            [f"{name.lower()}_"] * (len(df_fields)),
            ([f"{field}" for field in df_fields]),
        )
    ]

    required_cols = ["google_places_place_id"]

    # fields that are accessed directly from the api
    api_fields = ["website", "type", "reviews"]

    # Output fields are not necessarily the same as input fields
    api_fields_output = ["website", "types"]

    gmaps = None

    def load_data(self) -> None:
        # don't perform this in class body or else it will fail in tests due to missing API key
        if GOOGLE_PLACES_API_KEY is None:
            raise StepError("An API key for Google Places is needed to run this step!")
        self.gmaps = googlemaps.Client(key=GOOGLE_PLACES_API_KEY)

    def verify(self) -> bool:
        return super().verify() and GOOGLE_PLACES_API_KEY is not None

    def run(self) -> pd.DataFrame:
        # Call places API
        tqdm.pandas(desc="Getting info from Places API")
        self.df[
            [f"{self.name.lower()}_{field}" for field in self.df_fields]
        ] = self.df.progress_apply(
            lambda lead: self.get_data_from_detailed_google_api(lead), axis=1
        )

        return self.df

    def finish(self) -> None:
        pass

    def get_data_from_detailed_google_api(self, lead_row):
        error_return_value = pd.Series([None] * len(self.df_fields))

        place_id = lead_row["google_places_place_id"]

        if place_id is None or pd.isna(place_id):
            return error_return_value

        # Call for the detailed API using specified fields
        try:
            # Fetch place details including reviews
            response = self.gmaps.place(
                place_id,
                fields=self.api_fields,
                language="original",
                reviews_no_translations=True,
            )

            # Check response status
            if response.get("status") != HTTPStatus.OK.name:
                log.warning(
                    f"Failed to fetch data. Status code: {response.get('status')}"
                )
                return error_return_value

        except RequestException as e:
            log.error(f"Error: {str(e)}")

        except (ApiError, HTTPError, Timeout, TransportError) as e:
            error_message = (
                str(e.message)
                if hasattr(e, "message") and e.message is not None
                else str(e)
            )
            log.warning(f"Error: {error_message}")

        reviews = []

        if "result" in response and "reviews" in response["result"]:
            reviews = response["result"]["reviews"]

        get_database().save_review(reviews, place_id)

        results_list = [
            response["result"][field] if field in response["result"] else None
            for field in self.api_fields_output
        ]

        return pd.Series(results_list)
