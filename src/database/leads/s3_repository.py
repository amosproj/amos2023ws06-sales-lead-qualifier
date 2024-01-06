# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Sophie Heasman <sophieheasmann@gmail.com>

import csv
import hashlib
import json
from datetime import datetime
from io import StringIO

import boto3
import botocore.exceptions
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
    BUCKET = "amos--data--events"
    DF_INPUT = f"s3://{BUCKET}/leads/enriched.csv"
    DF_OUTPUT = f"s3://{BUCKET}/leads/enriched.csv"
    REVIEWS = f"s3://{BUCKET}/reviews/"
    SNAPSHOTS = f"s3://{BUCKET}/snapshots/"
    LOOKUP_TABLES = f"s3://{BUCKET}/lookup_tables/"

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
                f"{e.response['Error']['Code']}: {e.response['Error']['Message']}"
                if "Error" in e.response
                else f"Error while getting object s3://{bucket}/{obj_key}"
            )

        return obj

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
            log.error(
                f"Error loading review from S3 with id {place_id}. Error: {str(e)}"
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
