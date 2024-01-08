# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lucca Baumgärtner <lucca.baumgaertner@fau.de>

import pandas as pd
from email_validator import EmailNotValidError, validate_email

from bdc.steps.helpers import get_lead_hash_generator
from bdc.steps.step import Step
from logger import get_logger

log = get_logger()


def extract_custom_domain(email: str) -> pd.Series:
    try:
        validate_email(email, check_deliverability=False)
        return pd.Series([email.split("@")[1], True])
    except EmailNotValidError as e:
        return pd.Series([None, False])


def analyze_email_account(lead) -> pd.Series:
    if not lead["email_valid"]:
        return pd.Series([False, False])
    email_account = lead["Email"].split("@")[0]
    first_name_in_account = (
        lead["First Name"].lower() in email_account.lower()
        if "First Name" in lead
        else False
    )
    last_name_in_account = (
        lead["Last Name"].lower() in email_account.lower()
        if "Last Name" in lead
        else False
    )
    return pd.Series([first_name_in_account, last_name_in_account])


class AnalyzeEmails(Step):
    """
    A pipeline step performing various preprocessing steps with the given email address.
    The following columns will be added on successful processing:

    - **domain**: The custom domain name/website if any
    - **email_valid**: Boolean result of email check
    - **first_name_in_account**: Boolean, True if the given first name is part of the email account name
    - **last_name_in_account**: Boolean, True if the given last name is part of the email account name

    Attributes:
        name: Name of this step, used for logging
        added_cols: List of fields that will be added to the main dataframe by executing this step
        required_cols: List of fields that are required to be existent in the input dataframe before performing this step
    """

    name = "Analyze-Emails"

    added_cols = [
        "domain",
        "email_valid",
        "first_name_in_account",
        "last_name_in_account",
    ]

    required_cols = ["Email", "First Name", "Last Name"]

    def load_data(self):
        pass

    def verify(self):
        return super().verify()

    def run(self):
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
        # extract domain from email
        # Possibly add the normalized email here
        # self.df[["domain", "email_valid"]] = self.df.apply(
        #     lambda lead: extract_custom_domain(str(lead["Email"])), axis=1
        # )

        self.df[["domain", "email_valid"]] = self.df.apply(
            lambda lead: get_lead_hash_generator().hash_check(
                lead,
                extract_custom_domain,
                self.name + "_Custom-Domains",
                ["domain", "email_valid"],
                str(lead["Email"]),
            ),
            axis=1,
        )

        self.df[["first_name_in_account", "last_name_in_account"]] = self.df.apply(
            lambda lead: get_lead_hash_generator().hash_check(
                lead,
                analyze_email_account,
                self.name + "_Email-Accounts",
                ["first_name_in_account", "last_name_in_account"],
                lead,
            ),
            axis=1,
        )

        # self.df[["first_name_in_account", "last_name_in_account"]] = self.df.apply(
        #     lambda lead: analyze_email_account(lead), axis=1
        # )

        # remove commercial domains
        self.df["domain"].replace(commercial_domains, None, inplace=True)
        return self.df

    def finish(self):
        p_custom_domains = self.df["domain"].notna().sum() / len(self.df) * 100
        log.info(f"Percentage of custom domains: {p_custom_domains:.2f}%")
