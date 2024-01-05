# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Ruchita Nathani <ruchita.nathani@fau.de>

import hashlib
import os

import pandas as pd

from bdc.steps.step import Step
from database import get_database
from logger import get_logger

log = get_logger()


class GenerateHashLeads:
    BASE_PATH = os.path.dirname(__file__)

    # def load_data(self):
    #     pass
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
        lookup_table = self.create_or_load_lookup_table(step)
        if lead_hash in lookup_table["HashedData"].tolist():
            # If the hash exists in the lookup table, return the corresponding data
            log.info(f"Hash {lead_hash} already exists in the lookup table.")
            breakpoint()
            return lead_data[fields_tofill]
        new_value = {
            "HashedData": lead_hash,
            "First Name": lead_data["First Name"],
            "Last Name": lead_data["Last Name"],
            "Company / Account": lead_data["Company / Account"],
            "Phone": lead_data["Phone"],
            "Email": lead_data["Email"],
        }
        lookup_table.loc[len(lookup_table)] = new_value
        self.save_lookup_table(lookup_table, step)

        return data_fill(*args, **kwargs)

    def save_lookup_table(self, lookup_table, step):
        lookup = os.path.abspath(
            os.path.join(self.BASE_PATH, f"../../data/{step}_lookup_table.csv")
        )
        lookup_table.to_csv(lookup, index=False)

    def create_or_load_lookup_table(self, step):
        lookup = os.path.abspath(
            os.path.join(self.BASE_PATH, f"../../data/{step}_lookup_table.csv")
        )
        try:
            # If the lookup table exists, load it
            # lookup_table = pd.read_csv("./data/lookup_table.csv")

            lookup_table = pd.read_csv(lookup)
        except FileNotFoundError:
            # If the lookup table doesn't exist, create an empty one
            lookup_table = pd.DataFrame(
                columns=[
                    "HashedData",
                    "First Name",
                    "Last Name",
                    "Company / Account",
                    "Phone",
                    "Email",
                ]
            )
            lookup_table.to_csv(lookup, index=False)
        return lookup_table

    def run(self):
        lookup_table = self.create_or_load_lookup_table()

        # Copy original dataframe to create a separate lookup table
        data_frame = get_database().get_dataframe()

        # Apply the hash function to each row and create a new column 'HashedData'
        data_frame["HashedData"] = data_frame.apply(self.hash_lead, axis=1)
        existing_hashes = lookup_table["HashedData"].tolist()
        leads_to_process = data_frame[~data_frame["HashedData"].isin(existing_hashes)]

        for index, lead in leads_to_process.iterrows():
            log.info(f"Processing lead with hash: {lead['HashedData']}")

            # Update the lookup table with the processed lead
            lookup_table = pd.concat(
                [lookup_table, lead.to_frame().transpose()], ignore_index=True
            )

        # Save the updated lookup table
        lookup_table.to_csv(self.lookup, index=False)

        log.info(f"Processing complete.")
        return self.df

    # def finish(self):
    #     pass
