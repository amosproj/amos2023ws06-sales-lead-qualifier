# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Sophie Heasman <sophieheasmann@gmail.com>

import json
import os
from datetime import datetime

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
    GPT_RESULTS = os.path.abspath(os.path.join(BASE_PATH, "../../data/gpt/"))

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
            f"{self.SNAPSHOTS}{prefix.replace('/','_')}{name.lower()}_snapshot.csv"
        )
        df.to_csv(full_path, index=False)

    def clean_snapshots(self, prefix):
        pass

    def save_gpt_result(self, gpt_result, file_id, operation_name, force_refresh=False):
        """
        Save the results of GPT operations to a specified path
        :param gpt_results: The results of the GPT operations to be saved
        :param operation_name: The name of the GPT operation
        :param save_date: The date the results were saved
        """
        file_name = file_id + "_gpt_results.json"
        json_file_path = self.GPT_RESULTS + file_name
        current_date = self._get_current_time_as_string()
        if os.path.exists(json_file_path):
            with open(json_file_path, "r", encoding="utf-8") as json_file:
                existing_data = json.load(json_file)

            existing_data[operation_name] = {
                "result": gpt_result,
                "last_update_date": current_date,
            }

            with open(json_file_path, "w", encoding="utf-8") as json_file:
                json.dump(existing_data, json_file, ensure_ascii=False, indent=4)
        else:
            with open(json_file_path, "w", encoding="utf-8") as json_file:
                json.dump(
                    {
                        operation_name: {
                            "result": gpt_result,
                            "last_update_date": current_date,
                        }
                    },
                    json_file,
                    ensure_ascii=False,
                    indent=4,
                )

    def fetch_gpt_result(self, file_id, operation_name):
        """
        Fetches the GPT result for a given file ID and operation name.

        Args:
            file_id (str): The ID of the file.
            operation_name (str): The name of the GPT operation.

        Returns:
            The GPT result for the specified file ID and operation name.
        """
        file_name = file_id + "_gpt_results.json"
        json_file_path = self.GPT_RESULTS + file_name
        try:
            with open(json_file_path, "r", encoding="utf-8") as json_file:
                data = json.load(json_file)
                return data[operation_name]
        except:
            log.warning(f"Error loading GPT results from path {json_file_path}.")
            # Return empty string if any exception occurred or status is not OK
            return ""
