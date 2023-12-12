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


def is_company_email(email):
    commercial_domains = [
        "web.de",
        "mail.com",
        "mail.de",
        "msn.com",
        "gmail.com",
        "yahoo.com",
        "hotmail.com",
        "aol.com",
        "hotmail.co.uk",
        "hotmail.fr",
        "yahoo.fr",
        "live.com",
        "gmx.de",
        "outlook.com",
        "icloud.com",
        "outlook.de",
        "online.de",
        "gmx.net",
        "googlemail.com",
        "yahoo.de",
        "t-online.de",
        "gmx.ch",
        "gmx.at",
        "hotmail.ch",
        "live.nl",
        "hotmail.de",
        "home.nl",
        "bluewin.ch",
        "freenet.de",
        "upcmail.nl",
        "zeelandnet.nl",
        "hotmail.nl",
        "arcor.de",
        "aol.de",
        "me.com",
        "gmail.con",
        "office.de",
        "my.com",
    ]

    if email.split("@")[1] in commercial_domains:
        return False
    else:
        return True


class FacebookGraphAPI(Step):
    name = "Facebook_Graph"
    added_cols = ["email", "category"]

    def load_data(self) -> None:
        pass

    def verify(self) -> bool:
        return (
            self.df is not None and "First Name" in self.df and "Last Name" in self.df
        )

    def run(self):
        # choosing company name as search query if email is not in commercial domain, otherwise choose first and last names
        self.df["search-query"] = self.df.apply(
            lambda row: row["Email"]
            if is_company_email(row["Email"])
            else row["First Name"] + " " + row["Last Name"],
            axis=1,
        )
        self.df["data-fields"] = self.df.apply(
            lambda row: ["category", "about", "location", "website"]
            if is_company_email(row["Email"])
            else ["email", "location"],
            axis=1,
        )

        tqdm.pandas(desc="Searching Facebook Graph API")
        try:
            self.df.progress_apply(self.search_facebook_graph, axis=1)
        except ValueError as e:
            log.error(f"Error: {e}")

        # delete the additional columns from the df at the end
        self.df.drop("search-query", axis=1, inplace=True)
        self.df.drop("data-fields", axis=1, inplace=True)

        return self.df

    def search_facebook_graph(self, row):
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
            search_results = graph.request(
                "/search", {"q": row["search-query"], "type": "user"}
            )
            if isinstance(search_results, dict) and search_results.get("data"):
                user = search_results["data"][0]
                user_id = user.get("id")
                user_details = graph.get_object(user_id, fields=row["data-fields"])
                log.debug(f"user_details={user_details}")

                for field in row["data-fields"]:
                    if field in graph.get_object(user_id):
                        data_found = graph.get_object(user_id)[row["data-fields"]]
                        log.debug(f"found {row['data-fields']}: {data_found}")
                        self.df[row["data-fields"]] = data_found
                    else:
                        log.info(
                            f"No user data fields found for {row['search-query']}!"
                        )
            else:
                log.info(
                    f"No users/pages found with the given name {row['search-query']}!"
                )
        except facebook.GraphAPIError as e:
            log.error(f"Graph API Error: {e}")

    def finish(self) -> None:
        pass
