# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Berkay Bozkurt <resitberkaybozkurt@gmail.com>

from deutschland.bundesanzeiger import Bundesanzeiger
from pandas import DataFrame
from tqdm import tqdm

from bdc.steps.step import Step
from logger import get_logger


class BundesAPI(Step):
    name = "BundesAPI"
    required_cols = ["Company / Account"]
    added_cols = []
    bundes_anzeiger = None

    def verify(self) -> bool:
        return super().verify()

    def finish(self):
        pass

    def load_data(self):
        self.bundes_anzeiger = Bundesanzeiger()
        pass

    def run(self) -> DataFrame:
        tqdm.pandas(desc="Running BundesAPI for company names")
        self.df[self.added_cols] = self.df.progress_apply(
            lambda lead: self._extract_company_related_data(lead), axis=1
        )
        pass

    def _extract_company_related_data(self, lead):
        # TODO Implement the extract_company_related_data method

        pass

    def _search_in_bundesanzeiger(self, company_name):
        # TODO Implement the search_in_bundesanzeiger method
        pass
