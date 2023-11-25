# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Fabian-Paul Utech <f.utech@gmx.net>

from typing import Optional

import pandas as pd
import phonenumbers
from phonenumbers import geocoder

from bdc.steps.step import Step
from logger import get_logger

log = get_logger()


class PreprocessPhonenumbers(Step):
    name = "Preprocess-Phonenumbers"
    added_cols = [
        "number_formatted",
        "number_country",
        "number_area",
        "number_valid",
        "number_possible",
    ]

    def load_data(self):
        pass

    def verify(self):
        return "Phone" in self._df

    def run(self):
        number_features = {col: [] for col in self.added_cols}

        # Define a lambda function for each row of the df
        process_row = lambda row: self.check_number("+" + str(row["Phone"])) or {
            key: False if "valid" in key or "possible" in key else ""
            for key in number_features
        }

        # Apply the lambda function and save the resulting dictionaries in a pd.series
        sr_features = self.df.apply(process_row, axis=1)

        # Apply on the pd.Series the pd.Series to create a df with new columns for each key
        df_features = sr_features.apply(pd.Series)

        # Concatenate the original DataFrame with the new DataFrame
        self.df = pd.concat([self.df, df_features], axis=1)

        return self.df

    def finish(self):
        p_phone_numbers = self._df["number_valid"].sum() / len(self._df) * 100
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
