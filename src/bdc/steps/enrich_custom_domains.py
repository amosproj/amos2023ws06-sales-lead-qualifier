# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lucca Baumgärtner <lucca.baumgaertner@fau.de>

import pandas as pd
from email_validator import validate_email, EmailNotValidError
from typing import Optional
from bdc.steps.step import Step


class EnrichCustomDomains(Step):
    name = "Custom-Domains"

    def load_data(self):
        pass

    def verify(self):
        return "Email" in self._df

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
        ]
        # extract domain from email
        # Possibly add the normalized email here
        self._df["domain"] = self._df.apply(lambda row: self.check_valid_email(str(row["Email"])), axis=1)

        # remove commercial domains
        self._df["domain"].replace(commercial_domains, None, inplace=True)
        return self.df

    def finish(self):
        # print(self.df.head())
        p_custom_domains = self._df["domain"].notna().sum() / len(self._df) * 100
        self.log(f"Percentage of custom domains: {p_custom_domains:.2f}%")
        # print(self._df["domain"].value_counts(sort=True))
    
    def check_valid_email(self, email: str) -> Optional[str]:
        try:
            validate_email(email,check_deliverability=False)
            return email.split("@")[1]
        except EmailNotValidError as e:
            return None
