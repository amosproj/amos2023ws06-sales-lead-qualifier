# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Sophie Heasman <sophieheasmann@gmail.com>

import csv
import json
import os
from pathlib import Path

import joblib
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
    DF_PREPROCESSED_INPUT = os.path.abspath(
        os.path.join(BASE_PATH, "../../data/preprocessed_data_files/")
    )
    DF_PREDICTION_OUTPUT = os.path.abspath(
        os.path.join(BASE_PATH, "../../data/leads_predicted_size.csv")
    )
    REVIEWS = os.path.abspath(os.path.join(BASE_PATH, "../../data/reviews/"))
    SNAPSHOTS = os.path.abspath(os.path.join(BASE_PATH, "../../data/snapshots/"))
    GPT_RESULTS = os.path.abspath(os.path.join(BASE_PATH, "../../data/gpt-results/"))
    ML_MODELS = os.path.abspath(os.path.join(BASE_PATH, "../../data/models/"))
    CLASSIFICATION_REPORTS = os.path.abspath(
        os.path.join(BASE_PATH, "../../data/classification_reports/")
    )

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

    def save_prediction(self, df):
        """
        Save dataframe in df parameter in chosen output location
        """
        df.to_csv(self.DF_PREDICTION_OUTPUT, index=False)
        log.info(f"Saved prediction result locally to {self.DF_PREDICTION_OUTPUT}")

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
        file_name = place_id + "_gpt_results.json"
        json_file_path = os.path.join(self.REVIEWS, file_name)

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
        file_name = place_id + "_gpt_results.json"
        reviews_path = os.path.join(self.REVIEWS, file_name)
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
                    "Last Updated",
                ]
            )  # Write the header

            for hashed_data, other_columns in lookup_table.items():
                csv_writer.writerow([hashed_data] + other_columns)

    def load_lookup_table(self, step_name: str) -> dict:
        lookup_path = Path(
            self.BASE_PATH + f"/../../data/lookup_tables/{step_name}.csv"
        )
        if not lookup_path.resolve().parent.exists():
            lookup_path.resolve().parent.mkdir(parents=True, exist_ok=True)
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

    def save_gpt_result(self, gpt_result, file_id, operation_name, force_refresh=False):
        """
        Save the results of GPT operations to a specified path
        :param gpt_results: The results of the GPT operations to be saved
        :param operation_name: The name of the GPT operation
        :param save_date: The date the results were saved
        """
        file_name = file_id + "_gpt_results.json"
        json_file_path = os.path.join(self.GPT_RESULTS, file_name)

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
        json_file_path = os.path.join(self.GPT_RESULTS, file_name)
        if not os.path.exists(json_file_path):
            return ""
        try:
            with open(json_file_path, "r", encoding="utf-8") as json_file:
                data = json.load(json_file)
                if operation_name not in data:
                    log.info(
                        f"Data for operation {operation_name} was not found in {json_file_path}"
                    )
                    return ""
                return data[operation_name]
        except:
            log.warning(f"Error loading GPT results from path {json_file_path}.")
            # Return empty string if any exception occurred or status is not OK
            return ""

    def load_ml_model(self, model_name: str):
        model_file_path = os.path.join(self.ML_MODELS, model_name)
        try:
            model = joblib.load(open(model_file_path, "rb"))
        except FileNotFoundError:
            log.error(f"Could not find model file {model_file_path}")
            model = None

        return model

    def save_ml_model(self, model, model_name: str):
        if not os.path.exists(self.ML_MODELS):
            Path(self.ML_MODELS).mkdir(parents=True, exist_ok=True)
        model_file_path = os.path.join(self.ML_MODELS, model_name)
        if os.path.exists(model_file_path):
            log.warning(f"Overwriting model at {model_file_path}")
        try:
            joblib.dump(model, open(model_file_path, "wb"))
        except Exception as e:
            log.error(f"Could not save model at {model_file_path}! Error: {str(e)}")

    def load_classification_report(self, model_name: str):
        report_file_path = os.path.join(
            self.CLASSIFICATION_REPORTS, "report_" + model_name
        )
        try:
            report = joblib.load(open(report_file_path, "rb"))
        except FileNotFoundError:
            log.error(f"Could not find report file {report_file_path}")
            report = None

        return report

    def save_classification_report(self, report, model_name: str):
        if not os.path.exists(self.CLASSIFICATION_REPORTS):
            Path(self.CLASSIFICATION_REPORTS).mkdir(parents=True, exist_ok=True)
        report_file_path = os.path.join(
            self.CLASSIFICATION_REPORTS, "report_" + model_name
        )
        if os.path.exists(report_file_path):
            log.warning(f"Overwriting report at {report_file_path}")
        try:
            joblib.dump(report, open(report_file_path, "wb"))
        except Exception as e:
            log.error(f"Could not save report at {report_file_path}! Error: {str(e)}")

    def get_preprocessed_data_path(self, historical: bool = True):
        file_name = (
            "historical_preprocessed_data.csv"
            if historical
            else "preprocessed_data.csv"
        )
        file_path = os.path.join(self.DF_PREPROCESSED_INPUT, file_name)
        return file_path

    def load_preprocessed_data(self, historical: bool = True):
        try:
            return pd.read_csv(self.get_preprocessed_data_path(historical))
        except FileNotFoundError:
            log.error("Error: Could not find input file for preprocessed data.")
