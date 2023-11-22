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
from googlemaps.exceptions import ApiError, HTTPError, Timeout, TransportError
from requests import RequestException
from tqdm import tqdm

from bdc.steps.step import Step, StepError
from config import GOOGLE_PLACES_API_KEY


class GooglePlaces(Step):
    name = "Google_Places"
    URL = "https://maps.googleapis.com/maps/api/place/textsearch/json?query="

    # fields that are expected as an output of the df.apply lambda function
    df_fields = [
        "place_id",
        "business_status",
        "formatted_address",
        "name",
        "user_ratings_total",
        "rating",
        "price_level",
        "candidate_count_mail",
        "candidate_count_phone",
        "place_id_matches_phone_search",
        "confidence",
    ]
    # fields that are accessed directly from the api
    api_fields = [
        "place_id",
        "business_status",
        "formatted_address",
        "name",
        "user_ratings_total",
        "rating",
        "price_level",
    ]

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
            and "number_formatted" in self.df
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
        p_matches = (
            self._df["google_places_place_id_matches_phone_search"].sum()
            / len(self._df)
            * 100
        )
        p_matches_rel = (
            self._df["google_places_place_id_matches_phone_search"].notna().sum()
            / len(self._df["google_places_place_id_matches_phone_search"].notna())
            * 100
        )
        self.log(
            f"Percentage of mail search matching phone search (of all): {p_matches:.2f}%"
        )
        self.log(
            f"Percentage of mail search matching phone search (at least one result): {p_matches_rel:.2f}%"
        )

    def get_data_from_google_api(self, lead_row):
        """Request Google Places Text Search API"""
        error_return_value = pd.Series([None] * len(self.df_fields))

        search_query = lead_row["domain"]

        phone_number = lead_row["number_formatted"]

        if search_query is None and lead_row["email_valid"]:
            account_name = lead_row["Email"].split("@")[0]
            if not (
                lead_row["first_name_in_account"] and lead_row["last_name_in_account"]
            ):
                # use account name as search query and replace special characters with whitespace
                search_query = re.sub(r"[^a-zA-Z0-9\n]", " ", account_name)

        if search_query is None and phone_number is None:
            # if account name consists only of first and last name and no custom domain is available,
            # skip the search as no results are expected
            return error_return_value

        response_by_mail, response_count_mail = self.get_first_place_candidate(
            search_query, "textquery"
        )

        response_by_phone, response_count_phone = self.get_first_place_candidate(
            phone_number, "phonenumber"
        )

        # compare the place_id, if it doesn't match just output results by email for now
        if response_by_mail is not None and response_by_phone is not None:
            place_id_matches_phone_search = (
                response_by_phone["place_id"] == response_by_mail["place_id"]
            )
        else:
            place_id_matches_phone_search = False

        chosen_response = (
            response_by_mail if response_by_mail is not None else response_by_phone
        )

        if chosen_response is None:
            return error_return_value

        results_list = [
            chosen_response[field] if field in chosen_response else None
            for field in self.api_fields
        ]

        # add number of candidates, which is not a direct field in the api response but can be derived from it
        results_list.append(response_count_mail)
        results_list.append(response_count_phone)

        # add boolean indicator whether search by phone result matches search by email
        results_list.append(place_id_matches_phone_search)

        # calculate confidence score for google places results
        results_list.append(self.calculate_confidence(results_list, lead_row))

        return pd.Series(results_list)

    def get_first_place_candidate(self, query, input_type) -> (dict, int):
        if query is None:
            return None, 0
        try:
            response = self.gmaps.find_place(query, input_type, fields=self.api_fields)

            # Retrieve response
            # response = requests.get(self.URL + domain + "&key=" + GOOGLE_PLACES_API_KEY)
        except RequestException as e:
            self.log(f"Error: {str(e)}")
            return None, 0
        except (ApiError, HTTPError, Timeout, TransportError) as e:
            self.log(f"Error: {str(e.message) if e.message is not None else str(e)}")
            return None, 0

        if not response["status"] == HTTPStatus.OK.name:
            self.log(f"Failed to fetch data. Status code: {response['status']}")
            return None, 0

        if "candidates" not in response or len(response["candidates"]) == 0:
            return None, 0

        top_result = response["candidates"][0]

        no_candidates = len(response["candidates"])

        return top_result, no_candidates

    def calculate_confidence(self, results_list, lead) -> float | None:
        """
        Calculate some confidence score, representing how sure we are to have found the correct Google Place
        (using super secret, patented AI algorithm :P)
        :param results_list:
        :return: confidence
        """
        if results_list[self.df_fields.index("place_id")] is None:
            # no result -> no confidence
            return None
        if results_list[self.df_fields.index("place_id_matches_phone_search")]:
            # phone search and email search returned same result -> this has to be it!
            return 0.99
        if (
            results_list[self.df_fields.index("candidate_count_mail")] == 0
            and results_list[self.df_fields.index("candidate_count_phone")] == 1
        ):
            # phone number is a pretty good identifier
            return 0.8
        if (
            results_list[self.df_fields.index("candidate_count_mail")] == 1
            and results_list[self.df_fields.index("candidate_count_phone")] == 0
        ):
            if lead["domain"] is not None:
                # a custom domain is also a pretty good identifier
                return 0.7
            else:
                # without a domain the account name is used for search which is often generic
                return 0.4
        if (
            results_list[self.df_fields.index("candidate_count_mail")] == 1
            and results_list[self.df_fields.index("candidate_count_phone")] == 1
        ):
            # only two results but different... what is that supposed to mean?
            return 0.2
        # we found more than 1 result for either search method -> low confidence
        return 0.1
