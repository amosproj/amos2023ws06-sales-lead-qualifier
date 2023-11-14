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
    # app credentials
    app_id = 1386886602242547
    app_secret = FACEBOOK_APP_SECRET
    access_token = FACEBOOK_SDK_GRAPH_API_KEY

    # create facebook session
    # graph = facebook.GraphAPI(app_id, app_secret)
    graph = facebook.GraphAPI(access_token, version=3.0)

    URL = graph.get_auth_url()

    first_name = "Sherlock"
    last_name = "Holmes"
    search_query = f"{first_name} {last_name}"
    # search_results = graph.search(q=search_query, type="user")
    search_results = graph.request("/search", {"q": search_query, "type": "user"})

    if search_results.get("data"):
        for user in search_results["data"]:
            user_id = user.get("id")
            user_details = graph.get_object(
                user_id, fields="id, name, email"
            )  # odify fields as needed
            print(user_details)
            if "email" in graph.get_object(user_id):
                user_email = graph.get_object(user_id)["email"]
                print(f"User Email: {user_email}")
    else:
        print("No users found.")

    # for user in search_results.get("data", []):
    #     print(user)
    #     print(graph.get_object(user["id"]))
    #     # Access the user's email (if the 'email' permission is granted)
    #     if "email" in graph.get_object(user["id"]):
    #         user_email = graph.get_object(user["id"])["email"]
    #         print(f"User Email: {user_email}")

    def load_data(self) -> None:
        pass

    def verify(self) -> bool:
        pass

    def run(self):
        pass

    def finish(self) -> None:
        pass
