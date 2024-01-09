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


class GooglePlacesNearby(Step):
    """
    The GooglePlacesDetailed step will try to gather detailed information for a given google business entry, identified
    by the place ID. This information could be the website link, the review text and the business type. Reviews will
    be saved to a separate location based on the persistence settings this could be local or AWS S3.

    Attributes:
        name: Name of this step, used for logging
        added_cols: List of fields that will be added to the main dataframe by executing this step
        required_cols: List of fields that are required to be existent in the input dataframe before performing this step
    """

    name = "Google_Places_Nearby"

    # fields that are expected as an output of the df.apply lambda function
    df_fields = ["no_similar_businesses"]

    # Weirdly the expression [f"{name}_{field}" for field in df_fields] gives an error as name is not in the scope of the iterator
    added_cols = [
        name + field
        for (name, field) in zip(
            [f"{name.lower()}_"] * (len(df_fields)),
            ([f"{field}" for field in df_fields]),
        )
    ]

    required_cols = [
        "google_places_detailed_coordinates",
        "google_places_detailed_type",
    ]

    # fields that are accessed directly from the api
    api_fields = []

    # Output fields are not necessarily the same as input fields
    api_fields_output = []

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
        tqdm.pandas(desc="Getting info from Nearby Places API")
        self.df[
            [f"{self.name.lower()}_{field}" for field in self.df_fields]
        ] = self.df.progress_apply(
            lambda lead: self.get_data_from_nearby_google_api(lead), axis=1
        )

        return self.df

    def finish(self) -> None:
        pass

    def get_data_from_nearby_google_api(self, lead_row):
        error_return_value = pd.Series([None] * len(self.df_fields))

        types = lead_row["google_places_detailed_type"]
        coords = lead_row["google_places_detailed_coordinates"]

        if types is None or pd.isna(types) or coords is None or pd.isna(coords):
            return error_return_value

        types = [
            business_type
            for business_type in types.split()
            if business_type not in ["point_of_interest", "establishment"]
        ]
        coords = coords.split()

        # Call for the nearby API using specified fields
        results = list()
        number_of_places = 0

        for business_type in types:
            try:
                # Fetch place details including reviews
                response = self.gmaps.places_nearby(
                    location=(coords[0], coords[1]),
                    radius=1000,
                    type=business_type,
                    language="original",
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

            results.append(response["results"])
            number_of_places += len(response["results"])

        results_list = [
            response["results"][field] if field in response["results"] else None
            for field in self.api_fields_output
        ]

        results_list.append(number_of_places)
        # Save nearby places in json - implement in repository

        return pd.Series(results_list)
