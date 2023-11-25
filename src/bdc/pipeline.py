# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lucca Baumgärtner <lucca.baumgaertner@fau.de>

import numpy as np
import pandas as pd

from bdc.steps.step import Step, StepError
from logger import get_logger

log = get_logger()


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
        try:
            if index_col is not None:
                self.df = pd.read_csv(input_location, index_col=index_col)
            else:
                self.df = pd.read_csv(input_location)
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
                if step.verify() and not step.check_data_presence():
                    step_df = step.run()
                    self.df = step_df
            except StepError as e:
                log.error(f"Step {step.name} failed! {e}")

            self.df = self.df.replace(np.nan, None)

            # cleanup
            step.finish()

        log.info(f"Pipeline finished running {len(self.steps)} steps!")
        try:
            log.debug(self.df.head())
            self.df.to_csv(self.output_location)
        except AttributeError as e:
            log.error(f"No datas to show/save! Error: {e}")
