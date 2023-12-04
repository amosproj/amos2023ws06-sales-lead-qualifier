# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Sophie Heasman <sophieheasmann@gmail.com>

import hashlib
from datetime import datetime
from io import StringIO

import boto3
import botocore.exceptions
import pandas as pd

from logger import get_logger

log = get_logger()
s3 = boto3.client("s3")


class DataAbstractionLayer:
    S3_BUCKET = "s3://amos--data--events/leads/enriched.csv"
    LOCAL_OUTPUT = "./data/leads_enriched.csv"

    def __init__(self, db_type=None):
        """
        Initialise DAL
        :param db_type: Database to be used for output. As of 04/12/23, it can be: S3, local
        """
        # Attributes for all data types
        self.db_type = db_type
        self.df = None

        # S3
        self.bucket = None
        self.obj_key = None

        if self.db_type == "S3" or self.db_type == "local":
            self._connect_s3()
        elif self.db_type == None:
            raise log.error("No output location selected.")
        elif self.db_type is not None:
            raise log.error("Unsupported database type")

    def _connect_s3(self):
        if not self.S3_BUCKET.startswith("s3://"):
            log.error(
                "S3 location has to be defined like this: s3://<BUCKET>/<OBJECT_KEY>"
            )
            return

        source = self.S3_BUCKET
        remote_dataset = None

        try:
            self.bucket, self.obj_key = self._decode_s3_url()
            remote_dataset = self.fetch_data_s3()
        except IndexError:
            log.error(
                "S3 location has to be defined like this: s3://<BUCKET>/<OBJECT_KEY>"
            )

        if remote_dataset is None or "Body" not in remote_dataset:
            log.error(
                f"Couldn't find dataset in S3 bucket {self.bucket} and key {self.obj_key}"
            )
            return
        else:
            source = remote_dataset["Body"]

        try:
            self.df = pd.read_csv(source)
        except FileNotFoundError:
            log.error("Error: Could not find input file for Pipeline.")

    def _fetch_data_s3(self):
        """
        Tries to read an object from S3.
        :return:
        """
        obj = None
        try:
            obj = s3.get_object(Bucket=self.bucket, Key=self.obj_key)
        except botocore.exceptions.ClientError as e:
            log.warning(
                f"{e.response['Error']['Code']}: {e.response['Error']['Message']}"
                if "Error" in e.response
                else f"Error while getting object s3://{self.bucket}/{self.object_key}"
            )

        return obj

    def _decode_s3_url(self):
        obj_identifier = self.S3_BUCKET.split("//")[1].split("/")
        bucket = obj_identifier[0]
        obj_key = "/".join(obj_identifier[1:])
        return bucket, obj_key

    def save_dataframe(self):
        if self.db_type == "S3":
            self._backup_data()
            csv_buffer = StringIO()
            self.df.to_csv(csv_buffer, index=False)
            s3.put_object(
                Bucket=self.bucket, Key=self.object_key, Body=csv_buffer.getvalue()
            )
            log.info(
                f"Successfully saved enriched leads to s3://{self.bucket}/{self.object_key}"
            )

        elif self.db_type == "local":
            self.df.to_csv(self.LOCAL_OUTPUT, index=False)
            log.info(f"Saved enriched data locally to {self.LOCAL_OUTPUT}")

    def _backup_data(self):
        # Backup remote data before overwriting. Not completed locally
        if self.db_type == "S3":
            old_leads = self._fetch_data_s3()
            if old_leads is None or "Body" not in old_leads:
                return

            old_hash = hashlib.md5(old_leads["Body"].read()).hexdigest()
            backup_key = "backup/" + datetime.now().strftime(
                "%Y/%m/%d/%H%M%S_" + old_hash + ".csv"
            )
            source = {"Bucket": self.bucket, "Key": "leads/enriched.csv"}
            s3.copy(source, self.bucket, backup_key)
            log.info(f"Successful backup to s3://{self.bucket}/{backup_key}")

    def get_dataframe(self):
        return self.df

    def set_dataframe(self, df):
        self.df = df

    def insert_data(self, data):
        if self.db_type == "S3":
            # TODO: Insert data into S3. When the database is bigger, it might make more sense to insert new data
            # instead of replacing the database/downloading the whole database
            print("Data inserted into S3")
