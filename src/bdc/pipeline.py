# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lucca Baumgärtner <lucca.baumgaertner@fau.de>

import boto3
import pandas as pd

from bdc.steps import AnalyzeEmails, GooglePlaces, PreprocessPhonenumbers
from bdc.steps.step import Step, StepError
from logger import get_logger

log = get_logger()
s3 = boto3.client("s3")

S3_BUCKET = "amos--data--events"


class Pipeline:
    def __init__(
        self,
        steps,
        input_location: str,
        output_location: str = None,
        limit: int = None,
        index_col: int = None,
    ):
        self.steps: list[Step] = steps
        self.limit: int = limit

        # try to read most current dataset from S3 first
        remote_dataset = fetch_remote_data()

        # fallback if remote access was not possible
        if remote_dataset is None or "Body" not in remote_dataset:
            log.info(
                f"Couldn't find dataset in S3 bucket {S3_BUCKET}, falling back to local."
            )
            source = input_location
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

        self.output_location = (
            input_location if output_location is None else output_location
        )

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
                data_present = step.check_data_presence()
                if verified and not data_present:
                    step_df = step.run()
                    self.df = step_df
            except StepError as e:
                log.error(f"Step {step.name} failed! {e}")

            # cleanup
            step.finish()

        # database connection TODO: replace this connection to appropriate file
        # collection = mongo_connection("google_places")
        # collection.insert_one(top_result)

        self.df.to_csv(self.output_location)
        log.info(f"Pipeline finished running {len(self.steps)} steps!")
        try:
            log.debug(self.df.head())
            self.df.to_csv(self.output_location)
        except AttributeError as e:
            log.error(f"No datas to show/save! Error: {e}")


def fetch_remote_data():
    object_key = "leads/enriched.csv"
    obj = None
    try:
        obj = s3.get_object(Bucket=S3_BUCKET, Key=object_key)
    except (s3.exceptions.NoSuchKey, s3.exceptions.InvalidObjectState) as e:
        log.warning(e)
    return obj


if __name__ == "__main__":
    res = fetch_remote_data()
    print(res)

    p = Pipeline(
        steps=[AnalyzeEmails(), PreprocessPhonenumbers(), GooglePlaces()],
        input_location="s3",
        limit=20,
    )

    p.run()
