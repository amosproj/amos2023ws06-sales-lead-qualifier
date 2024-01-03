# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Berkay Bozkurt <resitberkaybozkurt@gmail.com>

from bdc.steps.step import Step


class BundesAPI(Step):
    name = "BundesAPI"
    required_cols = ["Company / Account"]
    added_cols = []

    def verify(self) -> bool:
        return super().verify()

    def finish(self):
        pass

    def load_data(self):
        # TODO: Implement the load_data method
        pass

    def run(self):
        # TODO: Implement the run method
        pass
