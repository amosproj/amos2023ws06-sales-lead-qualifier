# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Ruchita Nathani <ruchita.nathani@fau.de>

import hashlib
import os
from datetime import datetime

import pandas as pd

from bdc.steps.step import Step
from database import get_database
from logger import get_logger

log = get_logger()


class LeadHashGenerator:
    BASE_PATH = os.path.dirname(__file__)
    _curr_lookup_table = ("", None)

    def hash_lead(self, lead_data):
        # Concatenate key lead information
        data_to_hash = (
            str(lead_data["First Name"])
            + str(lead_data["Last Name"])
            + str(lead_data["Company / Account"])
            + str(lead_data["Phone"])
            + str(lead_data["Email"])
        )

        # Hash the concatenated string using SHA-256
        lead_hash = hashlib.sha256(data_to_hash.encode()).hexdigest()

        return lead_hash

    def hash_check(
        self,
        lead_data: pd.Series,
        data_fill_function: callable,
        step_name: str,
        fields_tofill: list[str],
        *args,
        **kwargs,
    ):
        if "lead_hash" in lead_data.to_list() and not pd.isna(lead_data["lead_hash"]):
            lead_hash = lead_data["lead_hash"]
        else:
            lead_hash = self.hash_lead(lead_data)
        if self._curr_lookup_table[0] != step_name:
            self._curr_lookup_table = (
                step_name,
                get_database().load_lookup_table(step_name),
            )

        lookup_table = self._curr_lookup_table[1]

        if lead_hash in lookup_table:
            # If the hash exists in the lookup table, return the corresponding data
            log.info(f"Hash {lead_hash} already exists in the lookup table.")
            try:
                previous_data = lead_data[fields_tofill]
                return previous_data
            except KeyError as e:
                log.info(
                    f"Hash is present but data fields {fields_tofill} were not found."
                )
                lookup_table[lead_hash] = lookup_table[lead_hash][:-1] + [
                    datetime.now().strftime("%Y-%m-%d_%H:%M:%S"),
                ]
                get_database().save_lookup_table(lookup_table, step_name)
                return data_fill_function(*args, **kwargs)

        lookup_table[lead_hash] = [
            lead_data["First Name"],
            lead_data["Last Name"],
            lead_data["Company / Account"],
            lead_data["Phone"],
            lead_data["Email"],
            datetime.now().strftime("%Y-%m-%d_%H:%M:%S"),
        ]
        get_database().save_lookup_table(lookup_table, step_name)

        return data_fill_function(*args, **kwargs)