# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lucca Baumgärtner <lucca.baumgaertner@fau.de>
# SPDX-FileCopyrightText: 2023 Sophie Heasman <sophieheasmann@gmail.com>

import numpy as np

from bdc.steps.step import Step, StepError
from database import get_database
from logger import get_logger

log = get_logger()


class Pipeline:
    def __init__(
        self,
        steps,
        limit: int = None,
    ):
        self.steps: list[Step] = steps
        self.limit: int = limit
        self.df = get_database().get_dataframe()

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
        get_database().set_dataframe(self.df)

        # Upload DAL dataframe to chosen database
        get_database().save_dataframe()

        log.info(f"Pipeline finished running {len(self.steps)} steps!")
