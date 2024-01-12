# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

import pandas as pd
from pandas import DataFrame
from tqdm import tqdm

from bdc.steps.helpers import get_lead_hash_generator
from bdc.steps.step import Step
from logger import get_logger

log = get_logger()


class HashGenerator(Step):
    """
    A pipeline step computing the hashed value of a lead using the basic data that should
    be present for every lead. These data include:

    - First Name
    - Last Name
    - Company / Account
    - Phone
    - Email

    Attributes:
        name: Name of this step, used for logging
        added_cols: List of fields that will be added to the main dataframe by executing this step
        required_cols: List of fields that are required to be existent in the input dataframe before performing this step
    """

    name = "Hash-Generator"

    added_cols = ["lead_hash"]

    required_cols = [
        "First Name",
        "Last Name",
        "Company / Account",
        "Phone",
        "Email",
    ]

    def load_data(self) -> None:
        pass

    def verify(self) -> bool:
        return super().verify()

    def run(self) -> DataFrame:
        tqdm.pandas(desc="Generating hash values for all leads")

        # This step cannot be used with the hash_check as it produces the hashes
        self.df["lead_hash"] = self.df.progress_apply(
            lambda lead: get_lead_hash_generator().hash_lead(lead), axis=1
        )

        return self.df

    def finish(self) -> None:
        p_hashes_generated = self.df["lead_hash"].notna().sum() / len(self.df) * 100
        log.info(f"Percentage of hashes generated: {p_hashes_generated:.2f}%")
