# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Ruchita Nathani <ruchita.nathani@fau.de>

import hashlib
import os

import pandas as pd

from bdc.steps.step import Step
from database import get_database
from logger import get_logger

log = get_logger()


class LeadHashGenerator:
    BASE_PATH = os.path.dirname(__file__)

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
        hash = hashlib.sha256(data_to_hash.encode()).hexdigest()

        return hash

    def hash_check(self, lead_data, data_fill, step, fields_tofill, *args, **kwargs):
        lead_hash = self.hash_lead(lead_data)
        lookup_table = get_database().create_or_load_lookup_table(step)
        if lead_hash in lookup_table["HashedData"].tolist():
            # If the hash exists in the lookup table, return the corresponding data
            log.info(f"Hash {lead_hash} already exists in the lookup table.")
            try:
                previous_data = lead_data[fields_tofill]
                return previous_data
            except KeyError as e:
                log.info(
                    f"Hash is present but data fields {fields_tofill} were not found."
                )
                return data_fill(*args, **kwargs)
        new_value = {
            "HashedData": lead_hash,
            "First Name": lead_data["First Name"],
            "Last Name": lead_data["Last Name"],
            "Company / Account": lead_data["Company / Account"],
            "Phone": lead_data["Phone"],
            "Email": lead_data["Email"],
        }
        lookup_table.loc[len(lookup_table)] = new_value
        get_database().save_lookup_table(lookup_table, step)

        return data_fill(*args, **kwargs)
