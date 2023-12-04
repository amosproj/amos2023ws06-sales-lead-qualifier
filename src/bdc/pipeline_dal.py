# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lucca Baumgärtner <lucca.baumgaertner@fau.de>
import hashlib
from datetime import datetime
from io import StringIO

import boto3
import numpy as np
import pandas as pd

from bdc.steps.step import Step, StepError
from database_abstraction_layer import DataAbstractionLayer
from logger import get_logger

log = get_logger()
s3 = boto3.client("s3")


class PipelineDAL:
    def __init__(
        self,
        steps,
        db: str = None,
        limit: int = None,
    ):
        self.steps: list[Step] = steps
        self.limit: int = limit
        self.df = None

        if db == "S3" and limit is not None:
            log.error(f"Only the full dataset can be saved to S3!")
            return

        # Initialise DAL, then save df in Pipeline
        self.data_abstraction_layer = DataAbstractionLayer(db)
        self.df = self.data_abstraction_layer.get_dataframe()

        if limit is not None:
            self.df = self.df[:limit]

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

        # Set dataframe in DAL
        self.data_abstraction_layer.set_dataframe(self.df)

        # Upload DAL dataframe to chosen database
        self.data_abstraction_layer.save_dataframe()

        log.info(f"Pipeline finished running {len(self.steps)} steps!")
