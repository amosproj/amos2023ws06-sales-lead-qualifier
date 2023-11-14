# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Ahmed Sheta <ahmed.sheta@fau.de>

from http import HTTPStatus

import facebook
import pandas as pd
import requests
from requests import RequestException
from tqdm import tqdm

from bdc.steps.step import Step
from config import FACEBOOK_APP_SECRET, FACEBOOK_SDK_GRAPH_API_KEY


class FacebookGraphAPI(Step):
    name = "Facebook_Graph"

    def load_data(self) -> None:
        pass

    def verify(self) -> bool:
        return (
            self.df is not None and "First Name" in self.df and "Last Name" in self.df
        )

    def run(self):
        self.df["Full Name"] = self.df["First Name"] + " " + self.df["Last Name"]
        tqdm.pandas(desc="Searching Facebook")
        try:
            self.df["Full Name"].progress_apply(
                lambda lead: self.search_facebook_graph(lead)
            )
        except facebook.GraphAPIError as e:
            print(f"Graph API Error: {e}")

    def search_facebook_graph(self, full_name):
        search_results = None
        # app credentials
        app_id = 1386886602242547
        app_secret = FACEBOOK_APP_SECRET

        token_url = f"https://graph.facebook.com/oauth/access_token?client_id={app_id}&client_secret={app_secret}&grant_type=client_credentials"

        response = requests.get(token_url)
        if response.status_code == 200:
            # Extract the new access token from the response
            access_token = response.json()["access_token"]
            print(f"New Access Token: {access_token}")
        else:
            print("Failed to retrieve a new access token, tryng the initial")
            access_token = FACEBOOK_SDK_GRAPH_API_KEY

        desired_fields = "id, name, email"
        graph = facebook.GraphAPI(access_token)
        try:
            search_results = graph.request("/search", {"q": full_name, "type": "user"})
            if isinstance(search_results, dict) and search_results.get("data"):
                for user in search_results["data"]:
                    user_id = user.get("id")
                    user_details = graph.get_object(user_id, fields=desired_fields)
                print(user_details)
                if "email" in graph.get_object(user_id):
                    user_email = graph.get_object(user_id)["email"]
                    print(f"User Email: {user_email}")
            else:
                print(f"No users found with the given name {full_name}")
        except facebook.GraphAPIError as e:
            print(f"Graph API Error: {e}")

    def finish(self) -> None:
        pass
