# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Sophie Heasman <sophieheasmann@gmail.com>

import hashlib
import json
from datetime import datetime
from io import StringIO

import boto3
import botocore.exceptions
import pandas as pd

from database.DAL import DataAbstractionLayer
from logger import get_logger

log = get_logger()
s3 = boto3.client("s3")


class S3Database(DataAbstractionLayer):
    DF_INPUT = "s3://amos--data--events/leads/enriched.csv"
    DF_OUTPUT = "s3://amos--data--events/test/leads/enriched.csv"
    REVIEWS = "s3://amos--data--events/reviews/"

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
            bucket, obj_key = self._decode_s3_url(self.DF_INPUT)
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

    def _decode_s3_url(self, url):
        """
        Retrieve the bucket and object key from object url
        :return: bucket string, object key string
        """
        obj_identifier = url.split("//")[1].split("/")
        bucket = obj_identifier[0]
        obj_key = "/".join(obj_identifier[1:])
        return bucket, obj_key

    def save_dataframe(self):
        """
        Save dataframe in df attribute in chosen output location
        """
        bucket, obj_key = self._decode_s3_url(self.DF_OUTPUT)
        self._backup_data()
        csv_buffer = StringIO()
        self.df.to_csv(csv_buffer, index=False)
        s3.put_object(
            Bucket=bucket,
            Key=obj_key,
            Body=csv_buffer.getvalue(),
        )
        log.info(f"Successfully saved enriched leads to s3://{bucket}/{obj_key}")

    def _backup_data(self):
        """
        Backup existing data to S3
        """
        bucket, obj_key = self._decode_s3_url(self.DF_OUTPUT)
        old_leads = self._fetch_object_s3(bucket, obj_key)
        if old_leads is None or "Body" not in old_leads:
            return

        old_hash = hashlib.md5(old_leads["Body"].read()).hexdigest()
        backup_key = "test/backup/" + datetime.now().strftime(
            "%Y/%m/%d/%H%M%S_" + old_hash + ".csv"
        )
        source = {"Bucket": bucket, "Key": "leads/enriched.csv"}
        s3.copy(source, bucket, backup_key)
        log.info(f"Successful backup to s3://{bucket}/{backup_key}")

    def insert_data(self, data):
        """
        TODO: Insert new data into specified dataframe
        :param data: Data to be inserted (desired format must be checked)
        """
        pass

    def save_review(self, review, place_id, force_refresh=False):
        """
        TODO: Upload review to specified review path
        :param review: json contents of the review to be uploaded
        """
        # Write the data to a JSON file
        file_name = place_id + "_reviews.json"
        bucket, key = self._decode_s3_url(self.REVIEWS)
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
        TODO: Fetch review for specified place_id
        :return: json contents of desired review
        """
        file_name = place_id + "_reviews.json"
        bucket, key = self._decode_s3_url(self.REVIEWS)
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
