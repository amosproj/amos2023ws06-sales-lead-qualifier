# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lucca Baumgärtner <lucca.baumgaertner@fau.de>

import numpy as np
import pandas as pd
from pandas import DataFrame

from bdc.steps.step import Step


class EnrichCustomDomains(Step):
    df: DataFrame

    def load_data(self):
        self.df = pd.read_csv(self._input_location)

    def verify(self):
        return "Email" in self.df

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
        ]
        # extract domain from email
        self.df["domain"] = self.df["Email"].str.split("@").str[1]

        # remove commercial domains
        self.df["domain"].replace(commercial_domains, np.nan, inplace=True)

    def finish(self):
        # print(self.df.head())
        p_custom_domains = self.df["domain"].notna().sum() / len(self.df) * 100
        print(f"Percentage of custom domains: {p_custom_domains:.2f}%")
        print(self.df["domain"].value_counts(sort=True))
