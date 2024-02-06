# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Sophie Heasman <sophieheasmann@gmail.com>

import csv
import hashlib
import json
import tempfile
from datetime import datetime
from io import StringIO

import boto3
import botocore.exceptions
import joblib
import pandas as pd

from config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
from logger import get_logger

from .repository import Repository

log = get_logger()
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)


def decode_s3_url(url):
    """
    Retrieve the bucket and object key from object url
    :return: bucket string, object key string
    """
    obj_identifier = url.split("//")[1].split("/")
    bucket = obj_identifier[0]
    obj_key = "/".join(obj_identifier[1:])
    return bucket, obj_key


class S3Repository(Repository):
    EVENTS_BUCKET = "amos--data--events"
    FEATURES_BUCKET = "amos--data--features"
    MODELS_BUCKET = "amos--models"
    DF_INPUT = f"s3://{EVENTS_BUCKET}/leads/enriched.csv"
    DF_OUTPUT = f"s3://{EVENTS_BUCKET}/leads/enriched.csv"
    DF_PREPROCESSED_INPUT = f"s3://{FEATURES_BUCKET}/preprocessed_data_files/"
    REVIEWS = f"s3://{EVENTS_BUCKET}/reviews/"
    SNAPSHOTS = f"s3://{EVENTS_BUCKET}/snapshots/"
    LOOKUP_TABLES = f"s3://{EVENTS_BUCKET}/lookup_tables/"
    GPT_RESULTS = f"s3://{EVENTS_BUCKET}/gpt-results/"
    ML_MODELS = f"s3://{MODELS_BUCKET}/models/"
    CLASSIFICATION_REPORTS = f"s3://{MODELS_BUCKET}/classification_reports/"

    def _download(self):
        """
        Download database from specified DF path
        """
        if not self.DF_INPUT.startswith("s3://") or not self.DF_OUTPUT.startswith(
            "s3://"
        ):
            log.error(
                "S3 location has to be defined like this: s3://<BUCKET>/<OBJECT_KEY>"
            )
            return

        source = None
        remote_dataset = None

        try:
            bucket, obj_key = decode_s3_url(self.DF_INPUT)
            remote_dataset = self._fetch_object_s3(bucket, obj_key)
        except IndexError:
            log.error(
                "S3 location has to be defined like this: s3://<BUCKET>/<OBJECT_KEY>"
            )

        if remote_dataset is None or "Body" not in remote_dataset:
            log.error(f"Couldn't find dataset in S3 bucket {bucket} and key {obj_key}")
            return
        else:
            source = remote_dataset["Body"]

        try:
            self.df = pd.read_csv(source)
        except FileNotFoundError:
            log.error("Error: Could not find input file for Pipeline.")

    def _fetch_object_s3(self, bucket, obj_key):
        """
        Tries to read an object from S3.
        :return: s3 object
        """
        obj = None
        try:
            obj = s3.get_object(Bucket=bucket, Key=obj_key)
        except botocore.exceptions.ClientError as e:
            log.warning(
                f"{e.response['Error']['Code']}: {e.response['Error']['Message']} (s3://{bucket}/{obj_key})"
                if "Error" in e.response
                else f"Error while getting object s3://{bucket}/{obj_key}"
            )

        return obj

    def _is_object_exists_on_S3(self, bucket, key):
        try:
            s3.head_object(Bucket=bucket, Key=key)
            return True
        except Exception as e:
            return False

    def _load_from_s3(self, bucket, key):
        """
        Load a file from S3
        :param bucket: The name of the S3 bucket
        :param key: The key of the object in the S3 bucket
        :return: The contents of the file
        """
        response = s3.get_object(Bucket=bucket, Key=key)
        file_content = response["Body"].read().decode("utf-8")
        return file_content

    def save_dataframe(self):
        """
        Save dataframe in df attribute in chosen output location
        """
        bucket, obj_key = decode_s3_url(self.DF_OUTPUT)
        self._backup_data()
        csv_buffer = StringIO()
        self.df.to_csv(csv_buffer, index=False)
        self._save_to_s3(csv_buffer.getvalue(), bucket, obj_key)
        log.info(f"Successfully saved enriched leads to s3://{bucket}/{obj_key}")

    def _save_to_s3(self, data, bucket, key):
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=data,
        )

    def _backup_data(self):
        """
        Backup existing data to S3
        """
        bucket, obj_key = decode_s3_url(self.DF_OUTPUT)
        old_leads = self._fetch_object_s3(bucket, obj_key)
        if old_leads is None or "Body" not in old_leads:
            return

        old_hash = hashlib.md5(old_leads["Body"].read()).hexdigest()
        backup_key = "backup/" + datetime.now().strftime(
            "%Y/%m/%d/%H%M%S_" + old_hash + ".csv"
        )
        source = {"Bucket": bucket, "Key": obj_key}
        try:
            s3.copy(source, bucket, backup_key)
        except botocore.exceptions.ClientError as e:
            log.warning(
                f"{e.response['Error']['Code']}: {e.response['Error']['Message']}"
                if "Error" in e.response
                else f"Error while backing up object s3://{bucket}/{obj_key}. Object does not exist"
            )

        log.info(f"Successful backup to s3://{bucket}/{backup_key}")

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
        bucket, key = decode_s3_url(self.REVIEWS)
        key += file_name

        try:
            # HeadObject throws an exception if the file doesn't exist
            s3.head_object(Bucket=bucket, Key=key)
            log.info(f"The file with key '{key}' exists in the bucket '{bucket}'.")

        except Exception as e:
            log.info(
                f"The file with key '{key}' does not exist in the bucket '{bucket}'."
            )
            # Upload the JSON string to S3
            reviews_str = json.dumps(review)
            s3.put_object(Body=reviews_str, Bucket=bucket, Key=key)
            log.info("reviews uploaded to s3")

    def fetch_review(self, place_id):
        """
        Fetch review for specified place_id
        :return: json contents of desired review
        """
        file_name = place_id + "_reviews.json"
        bucket, key = decode_s3_url(self.REVIEWS)
        key += file_name

        try:
            response = s3.get_object(Bucket=bucket, Key=key)
            file_content = response["Body"].read().decode("utf-8")
            json_content = json.loads(file_content)
            return json_content
        except Exception as e:
            log.info(
                f"No reviews in S3 for place with at s3://{bucket}/{key}. Error: {str(e)}"
            )
            return []

    def create_snapshot(self, df, prefix, name):
        full_path = f"{self.SNAPSHOTS}{prefix}{name}_snapshot.csv"
        bucket, key = decode_s3_url(full_path)

        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        self._save_to_s3(csv_buffer.getvalue(), bucket, key)

    def clean_snapshots(self, prefix):
        pass

    def save_lookup_table(self, lookup_table: dict, step_name: str) -> None:
        full_path = f"{self.LOOKUP_TABLES}{step_name}.csv"
        bucket, key = decode_s3_url(full_path)

        csv_buffer = StringIO()
        csv_writer = csv.writer(csv_buffer)
        # Write Header
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
        )
        # Write data rows
        for hashed_data, other_columns in lookup_table.items():
            csv_writer.writerow([hashed_data] + other_columns)

        self._save_to_s3(csv_buffer.getvalue(), bucket, key)

    def load_lookup_table(self, step_name: str) -> dict:
        file_name = f"{step_name}.csv"
        bucket, key = decode_s3_url(self.LOOKUP_TABLES)
        key += file_name

        lookup_table_s3_obj = self._fetch_object_s3(bucket, key)
        lookup_table = {}
        if lookup_table_s3_obj is None or "Body" not in lookup_table_s3_obj:
            log.info(f"Couldn't find lookup table in S3 bucket {bucket} and key {key}.")
            return lookup_table

        source = lookup_table_s3_obj["Body"]
        # Read the CSV content from S3 into a string
        csv_content = source.read().decode("utf-8")
        # Use StringIO to create a file-like object
        csv_buffer = StringIO(csv_content)
        # Use csv.reader to read the CSV content
        csv_reader = csv.reader(csv_buffer)
        header = next(csv_reader)
        for row in csv_reader:
            hashed_data = row[0]
            other_columns = row[1:]
            lookup_table[hashed_data] = other_columns
        return lookup_table

    def fetch_gpt_result(self, file_id, operation_name):
        """
        Fetches the GPT result for a given file ID and operation name from S3
        """
        # Define the file name and path
        file_name = f"{file_id}_gpt_result.json"
        full_url_path = f"{self.GPT_RESULTS}{file_name}"
        bucket, key = decode_s3_url(full_url_path)

        if not self._is_object_exists_on_S3(bucket, key):
            return None
        # Read data from s3
        existing_data = json.loads(self._load_from_s3(bucket, key))

        # check if the element with the operation name exists
        if operation_name in existing_data:
            return existing_data[operation_name]
        else:
            return None

    def save_gpt_result(self, gpt_result, file_id, operation_name, force_refresh=False):
        """
        Saves the GPT result for a given file ID and operation name on S3
        """
        # Define the file name and path
        file_name = f"{file_id}_gpt_result.json"
        full_url_path = f"{self.GPT_RESULTS}{file_name}"
        bucket, key = decode_s3_url(full_url_path)

        # Get current date and time
        current_time = self._get_current_time_as_string()

        # Prepare the data to be saved
        data_to_save = {"result": gpt_result, "last_update_date": current_time}

        # Check if the file already exists
        if self._is_object_exists_on_S3(bucket, key) and not force_refresh:
            # Load the existing data
            existing_data = json.loads(self._load_from_s3(bucket, key))

            # Update the existing data with the new result
            existing_data[operation_name] = data_to_save

            # Save the updated data back to S3
            self._save_to_s3(json.dumps(existing_data), bucket, key)
        else:
            # Save the new result to S3
            self._save_to_s3(json.dumps({operation_name: data_to_save}), bucket, key)

    def load_ml_model(self, model_name: str):
        file_name = f"{model_name}"
        bucket, key = decode_s3_url(self.ML_MODELS)
        key += file_name
        try:
            with tempfile.TemporaryFile() as fp:
                s3.download_fileobj(Fileobj=fp, Bucket=bucket, Key=key)
                fp.seek(0)
                model = joblib.load(fp)
            return model
        except Exception as e:
            log.error(f"Error loading model '{model_name}': {str(e)}")
            return None

    def save_ml_model(self, model, model_name: str):
        full_path = f"{self.ML_MODELS}{model_name}"
        bucket, key = decode_s3_url(full_path)
        try:
            with tempfile.TemporaryFile() as fp:
                joblib.dump(model, fp)
                fp.seek(0)
                s3.upload_fileobj(fp, bucket, key)
        except Exception as e:
            log.error(f"Could not save model for '{model_name}' to S3: {str(e)}")

    def load_classification_report(self, model_name: str):
        file_path = f"{self.CLASSIFICATION_REPORTS}report_{model_name}"
        bucket, key = decode_s3_url(file_path)

        try:
            with tempfile.TemporaryFile() as fp:
                s3.download_fileobj(Fileobj=fp, Bucket=bucket, Key=key)
                fp.seek(0)
                report = joblib.load(fp)
            return report
        except Exception as e:
            log.error(f"Error loading model '{model_name}': {str(e)}")
            return None

    def save_classification_report(self, report, model_name: str):
        file_path = f"{self.CLASSIFICATION_REPORTS}report_{model_name}"
        bucket, key = decode_s3_url(file_path)

        try:
            with tempfile.TemporaryFile() as fp:
                joblib.dump(report, fp)
                fp.seek(0)
                s3.upload_fileobj(fp, bucket, key)
        except Exception as e:
            log.error(f"Could not save report for '{model_name}' to S3: {str(e)}")

    def load_preprocessed_data(
        self, file_name: str = "historical_preprocessed_data.csv"
    ):
        file_path = self.DF_PREPROCESSED_INPUT + file_name
        if not file_path.startswith("s3://"):
            log.error(
                "S3 location has to be defined like this: s3://<BUCKET>/<OBJECT_KEY>"
            )
            return

        source = None
        remote_dataset = None

        try:
            bucket, obj_key = decode_s3_url(file_path)
            remote_dataset = self._fetch_object_s3(bucket, obj_key)
        except IndexError:
            log.error(
                "S3 location has to be defined like this: s3://<BUCKET>/<OBJECT_KEY>"
            )

        if remote_dataset is None or "Body" not in remote_dataset:
            log.error(f"Couldn't find dataset in S3 bucket {bucket} and key {obj_key}")
            return
        else:
            source = remote_dataset["Body"]

        try:
            return pd.read_csv(source)
        except FileNotFoundError:
            log.error("Error: Could not find input file for Pipeline.")
