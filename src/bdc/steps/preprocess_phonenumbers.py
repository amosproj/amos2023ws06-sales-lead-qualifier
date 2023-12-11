# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Fabian-Paul Utech <f.utech@gmx.net>

from typing import Optional

import pandas as pd
import phonenumbers
from phonenumbers import geocoder
from tqdm import tqdm

from bdc.steps.step import Step
from logger import get_logger

log = get_logger()


class PreprocessPhonenumbers(Step):
    """
    The PreprocessPhonenumbers step will check if the provided phone numbers are valid and extract geo information
    if possible.

    Attributes:
        name: Name of this step, used for logging
        added_cols: List of fields that will be added to the main dataframe by executing this step
        required_cols: List of fields that are required to be existent in the input dataframe before performing this
            step
    """

    name = "Preprocess-Phonenumbers"
    added_cols = [
        "number_formatted",
        "number_country",
        "number_area",
        "number_valid",
        "number_possible",
    ]
    required_cols = ["Phone"]

    def load_data(self):
        pass

    def verify(self):
        return self.df is not None and all(
            [col in self.df for col in self.required_cols]
        )

    def run(self):
        tqdm.pandas(desc="Preprocessing Phone numbers")
        self.df[self.added_cols] = self.df.progress_apply(
            lambda lead: pd.Series(self.process_row(lead)), axis=1
        )

        return self.df

    def process_row(self, row):
        return self.check_number("+" + str(row["Phone"])) or {
            key: False if "valid" in key or "possible" in key else ""
            for key in self.added_cols
        }

    def finish(self):
        p_phone_numbers = self.df["number_valid"].sum() / len(self.df) * 100
        log.info(f"Percentage of valid numbers: {p_phone_numbers}%")

    def check_number(self, phone_number: str) -> Optional[str]:
        try:
            phone_number_object = phonenumbers.parse(phone_number, None)
        except Exception as e:
            log.error(str(e))
            return None

        country_code = phonenumbers.format_number(
            phone_number_object, phonenumbers.PhoneNumberFormat.INTERNATIONAL
        ).split(" ")[0]
        international_number = phonenumbers.format_number(
            phone_number_object, phonenumbers.PhoneNumberFormat.INTERNATIONAL
        )

        # Set country based on country code (Norway and Finland not working properly, thats why they are defined separetly)
        country = {"+358": "Finland", "+47": "Norway"}.get(
            country_code, geocoder.country_name_for_number(phone_number_object, "en")
        )

        location = geocoder.description_for_number(phone_number_object, "en")
        location = "" if location == country else location

        # Valid number (e.g., it's in an assigned exchange)
        is_valid_number = phonenumbers.is_valid_number(phone_number_object)

        # Possible number (e.g., it has the right number of digits)
        is_possible_number = phonenumbers.is_possible_number(phone_number_object)

        results = [
            international_number,
            country,
            location,
            is_valid_number,
            is_possible_number,
        ]

        result_dict = {col: val for (col, val) in zip(self.added_cols, results)}

        return result_dict
