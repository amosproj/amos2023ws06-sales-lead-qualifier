# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lucca Baumgärtner <lucca.baumgaertner@fau.de>
import hashlib
from datetime import datetime
from io import StringIO

import boto3
import botocore.exceptions
import numpy as np
import pandas as pd

from bdc.steps.step import Step, StepError
from logger import get_logger

log = get_logger()
s3 = boto3.client("s3")


class Pipeline:
    def __init__(
        self,
        steps,
        input_location: str,
        output_location_local: str = None,
        output_location_remote: str = None,
        limit: int = None,
        index_col: int = None,
    ):
        self.steps: list[Step] = steps
        self.limit: int = limit
        self.df = None

        if (
            output_location_remote == "s3://amos--data--events/leads/enriched.csv"
            and limit is not None
        ):
            log.error(
                f"Only the full dataset can be saved to {output_location_remote}!"
            )
            return
        if (
            output_location_remote is not None
            and not output_location_remote.startswith("s3://")
        ):
            log.error(
                "S3 location has to be defined like this: s3://<BUCKET>/<OBJECT_KEY>"
            )
            return

        source = input_location

        if input_location.startswith("s3://"):
            remote_dataset = None
            bucket = None
            obj_key = None
            try:
                bucket, obj_key = decode_s3_url(input_location)
                remote_dataset = fetch_remote_data(bucket, obj_key)
            except IndexError:
                log.error(
                    "S3 location has to be defined like this: s3://<BUCKET>/<OBJECT_KEY>"
                )

            if remote_dataset is None or "Body" not in remote_dataset:
                log.error(
                    f"Couldn't find dataset in S3 bucket {bucket} and key {obj_key}"
                )
                return
            else:
                source = remote_dataset["Body"]

        try:
            if index_col is not None:
                self.df = pd.read_csv(source, index_col=index_col)
            else:
                self.df = pd.read_csv(source)
            if limit is not None:
                self.df = self.df[:limit]
        except FileNotFoundError:
            log.error("Error: Could not find input file for Pipeline.")
            self.df = None

        self.output_location_local = output_location_local
        self.output_location_remote = output_location_remote

    def run(self):
        if self.df is None:
            log.error(
                "Error: DataFrame of pipeline has not been initialized, aborting pipeline run!"
            )
            return
        # helper to pass the dataframe and/or input location from previous step to next step
        for step in self.steps:
            log.info(f"Processing step {step.name}")
            # load dataframe and/or input location for this step
            if step.df is None:
                step.df = self.df.copy()

            try:
                step.load_data()
                verified = step.verify()
                log.info(f"Verification for step {step.name}: {verified}")
                data_present = step.check_data_presence()
                if verified and not data_present:
                    step_df = step.run()
                    self.df = step_df

                    # cleanup
                    step.finish()
            except StepError as e:
                log.error(f"Step {step.name} failed! {e}")

            self.df = self.df.replace(np.nan, None)

        self.df.to_csv(self.output_location_local, index=False)
        log.info(f"Saved enriched data locally to {self.output_location_local}")

        if self.output_location_remote is not None:
            try:
                backup_remote_data()
                bucket, obj_key = decode_s3_url(self.output_location_remote)
                save_remote(self.df, bucket, obj_key)
                log.info(
                    f"Saved enriched data to S3 bucket={bucket} with key={obj_key}"
                )
            except IndexError:
                log.error(
                    "S3 location has to be defined like this: s3://<BUCKET>/<OBJECT_KEY>"
                )

        log.info(f"Pipeline finished running {len(self.steps)} steps!")


def fetch_remote_data(bucket, object_key):
    """
    Tries to read an object from S3.
    :param bucket: Bucket where to find the object
    :param object_key: Object key to read
    :return:
    """

    obj = None
    try:
        obj = s3.get_object(Bucket=bucket, Key=object_key)
    except botocore.exceptions.ClientError as e:
        log.warning(
            f"{e.response['Error']['Code']}: {e.response['Error']['Message']}"
            if "Error" in e.response
            else f"Error while getting object s3://{bucket}/{object_key}"
        )
    return obj


def save_remote(enriched_leads, bucket, object_key="leads/enriched.csv"):
    """
    Will save the new enriched leads dataframe to AWS and backup the existing one using the current time + file hash
    :param enriched_leads: Dataframe containing enriched leads
    :param bucket: S3 Bucket where the object is saved
    :param object_key: Object key used to save the object
    :return:
    """

    csv_buffer = StringIO()
    enriched_leads.to_csv(csv_buffer, index=False)
    s3.put_object(Bucket=bucket, Key=object_key, Body=csv_buffer.getvalue())
    log.info(f"Successfully saved enriched leads to s3://{bucket}/{object_key}")


def backup_remote_data(bucket="amos--data--events", object_key="leads/enriched.csv"):
    old_leads = fetch_remote_data(bucket, object_key)
    if old_leads is not None and "Body" in old_leads:
        old_hash = hashlib.md5(old_leads["Body"].read()).hexdigest()
        backup_key = "backup/" + datetime.now().strftime(
            "%Y/%m/%d/%H%M%S_" + old_hash + ".csv"
        )
        source = {"Bucket": bucket, "Key": "leads/enriched.csv"}
        s3.copy(source, bucket, backup_key)
        log.info(f"Successful backup to s3://{bucket}/{backup_key}")


def decode_s3_url(url):
    obj_identifier = url.split("//")[1].split("/")
    bucket = obj_identifier[0]
    obj_key = "/".join(obj_identifier[1:])
    return bucket, obj_key
