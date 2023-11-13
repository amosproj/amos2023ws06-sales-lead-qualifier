# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lucca Baumgärtner <lucca.baumgaertner@fau.de>

import pandas as pd

from bdc.steps.step import StepError


class Pipeline:
    def __init__(
        self, steps, input_location: str, output_location: str = None, limit: int = None
    ):
        self.steps = steps
        self.limit = limit
        try:
            self.df = pd.read_csv(input_location)
            if limit is not None:
                self.df = self.df[:limit]
        except FileNotFoundError:
            print("Error: Could not find input file for Pipeline.")
            self.df = None
        self.output_location = (
            input_location if output_location is None else output_location
        )

    def run(self):
        if self.df is None:
            print(
                "Error: DataFrame of pipeline has not been initialized, aborting pipeline run!"
            )
            return
        # helper to pass the dataframe and/or input location from previous step to next step
        for step in self.steps:
            # load dataframe and/or input location for this step
            if step.df is None:
                step.df = self.df.copy()

            step.load_data()
            if step.verify():
                try:
                    step_df = step.run()
                    self.df = step_df
                except StepError as e:
                    print(f"Step {step.name} failed!")

            # cleanup
            step.finish()

        print(f"[PIPELINE] - Finished running {len(self.steps)} steps!")
        print(self.df.head())

        self.df.to_csv(self.output_location)
