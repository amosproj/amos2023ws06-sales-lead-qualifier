# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Sophie Heasman <sophieheasmann@gmail.com>

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
    GPT_RESULTS = f"s3://{BUCKET}/gpt-results/"

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
