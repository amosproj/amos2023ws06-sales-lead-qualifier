# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Ahmed Sheta <ahmed.sheta@fau.de>

from http import HTTPStatus

import facebook
import pandas as pd
import requests
from tqdm import tqdm

from bdc.steps.step import Step
from config import FACEBOOK_APP_ID, FACEBOOK_APP_SECRET
from logger import get_logger

log = get_logger()


class FacebookGraphAPI(Step):
    name = "Facebook_Graph"
    added_cols = ["Full Name", "email"]

    def load_data(self) -> None:
        pass

    def verify(self) -> bool:
        return (
            self.df is not None and "First Name" in self.df and "Last Name" in self.df
        )

    def run(self):
        self.df["Full Name"] = self.df["First Name"] + " " + self.df["Last Name"]
        self.desired_fields = ["email"]
        for field in self.desired_fields:
            self.df[field] = None
        tqdm.pandas(desc="Searching Facebook Graph API")
        try:
            self.df["Full Name"].progress_apply(
                lambda lead: self.search_facebook_graph(lead)
            )
        except ValueError as e:
            log.error(f"Error: {e}")

        return self.df

    def search_facebook_graph(self, full_name):
        search_results = None
        access_token = None
        user_email = None
        # app credentials
        app_id = FACEBOOK_APP_ID
        app_secret = FACEBOOK_APP_SECRET

        token_url = f"https://graph.facebook.com/oauth/access_token?client_id={app_id}&client_secret={app_secret}&grant_type=client_credentials"

        response = requests.get(token_url)
        if response.status_code == HTTPStatus.OK:
            # Extract the new access token from the response
            access_token = response.json()["access_token"]
            log.info(f"New access token acquired")
        else:
            log.error(f"Failed to retrieve a new access token")
        graph = facebook.GraphAPI(access_token)
        try:
            search_results = graph.request("/search", {"q": full_name, "type": "user"})
            if isinstance(search_results, dict) and search_results.get("data"):
                user = search_results["data"][0]
                user_id = user.get("id")
                user_details = graph.get_object(user_id, fields=self.desired_fields)
                log.debug(f"user_details={user_details}")
                if "email" in graph.get_object(user_id):
                    user_email = graph.get_object(user_id)["email"]
                    log.debug(f"User Email: {user_email}")
                    self.df["email"] = user_email
                else:
                    log.info(f"No user email found for {full_name}!")
            else:
                log.info(f"No users found with the given name {full_name}!")
        except facebook.GraphAPIError as e:
            log.error(f"Graph API Error: {e}")

    def finish(self) -> None:
        pass
