# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lucca Baumgärtner <lucca.baumgaertner@fau.de>

import numpy as np
import pandas as pd

from bdc.steps.step import Step


class EnrichCustomDomains(Step):
    name = "Custom-Domains"

    def load_data(self):
        self._df = pd.read_csv(self._input_location)

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
        self._df["domain"] = self._df["Email"].str.split("@").str[1]

        # remove commercial domains
        self._df["domain"].replace(commercial_domains, np.nan, inplace=True)

    def finish(self):
        # print(self.df.head())
        p_custom_domains = self._df["domain"].notna().sum() / len(self._df) * 100
        self.log(f"Percentage of custom domains: {p_custom_domains:.2f}%")
        # print(self._df["domain"].value_counts(sort=True))
