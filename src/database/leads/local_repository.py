# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Sophie Heasman <sophieheasmann@gmail.com>

import csv
import json
import os
from pathlib import Path

import pandas as pd

from logger import get_logger

from .repository import Repository

log = get_logger()


class LocalRepository(Repository):
    BASE_PATH = os.path.dirname(__file__)
    DF_INPUT = os.path.abspath(
        os.path.join(BASE_PATH, "../../data/sumup_leads_email.csv")
    )
    DF_OUTPUT = os.path.abspath(
        os.path.join(BASE_PATH, "../../data/leads_enriched.csv")
    )
    REVIEWS = os.path.abspath(os.path.join(BASE_PATH, "../../data/reviews/"))
    SNAPSHOTS = os.path.abspath(os.path.join(BASE_PATH, "../../data/snapshots/"))

    def _download(self):
        """
        Download database from specified DF path
        """
        try:
            self.df = pd.read_csv(self.DF_INPUT)
        except FileNotFoundError:
            log.error("Error: Could not find input file for Pipeline.")

    def save_dataframe(self):
        """
        Save dataframe in df attribute in chosen output location
        """
        self.df.to_csv(self.DF_OUTPUT, index=False)
        log.info(f"Saved enriched data locally to {self.DF_OUTPUT}")

    def insert_data(self, data):
        """
        TODO: Insert new data into specified dataframe
        :param data: Data to be inserted (desired format must be checked)
        """
        pass

    def save_review(self, review, place_id, force_refresh=False):
        """
        Upload review to specified review path
        :param review: json contents of the review to be uploaded
        """
        # Write the data to a JSON file
        file_name = place_id + "_reviews.json"
        json_file_path = self.REVIEWS + file_name

        if os.path.exists(json_file_path):
            log.info(f"Reviews for {place_id} already exist")
            return

        with open(json_file_path, "w", encoding="utf-8") as json_file:
            json.dump(review, json_file, ensure_ascii=False, indent=4)

    def fetch_review(self, place_id):
        """
        Fetch review for specified place_id
        :return: json contents of desired review
        """
        reviews_path = self.REVIEWS + place_id + "_reviews.json"
        try:
            with open(reviews_path, "r", encoding="utf-8") as reviews_json:
                reviews = json.load(reviews_json)
                return reviews
        except:
            log.warning(f"Error loading reviews from path {reviews_path}.")
            # Return empty list if any exception occurred or status is not OK
            return []

    def create_snapshot(self, df, prefix, name):
        full_path = (
            f"{self.SNAPSHOTS}/{prefix.replace('/','_')}{name.lower()}_snapshot.csv"
        )
        df.to_csv(full_path, index=False)

    def clean_snapshots(self, prefix):
        pass

    def save_lookup_table(self, lookup_table: dict, step_name: str) -> None:
        lookup_path = Path(
            self.BASE_PATH + f"/../../data/lookup_tables/{step_name}.csv"
        )
        with open(str(lookup_path), mode="w", newline="", encoding="utf-8") as fh:
            csv_writer = csv.writer(fh)
            csv_writer.writerow(
                [
                    "HashedData",
                    "First Name",
                    "Last Name",
                    "Company / Account",
                    "Phone",
                    "Email",
                ]
            )  # Write the header

            for hashed_data, other_columns in lookup_table.items():
                csv_writer.writerow([hashed_data] + other_columns)

    def load_lookup_table(self, step_name: str) -> dict:
        lookup_path = Path(
            self.BASE_PATH + f"/../../data/lookup_tables/{step_name}.csv"
        )
        if not lookup_path.resolve().parent.exists():
            lookup_path.resolve().parent.mkdir(parents=True)

        lookup_table = {}
        try:
            with open(str(lookup_path), mode="r", encoding="utf-8") as fh:
                csv_reader = csv.reader(fh)
                headers = next(csv_reader)  # Read the header row

                for row in csv_reader:
                    hashed_data = row[0]
                    other_columns = row[1:]
                    lookup_table[hashed_data] = other_columns
        except FileNotFoundError:
            # if the file is not present then there is no lookup table => return empty dict
            pass

        return lookup_table
