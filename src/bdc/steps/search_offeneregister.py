# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Berkay Bozkurt <resitberkaybozkurt@gmail.com>

import pandas as pd
from pandas import DataFrame
from tqdm import tqdm

from bdc.steps.helpers import OffeneRegisterAPI, get_lead_hash_generator
from bdc.steps.step import Step
from logger import get_logger


class SearchOffeneRegister(Step):
    name = "OffeneRegister"
    required_cols = ["Last Name", "First Name"]
    added_cols = [
        "company_name",
        "company_objective",
        "company_capital",
        "company_capital_currency",
        "compan_address",
    ]
    offeneregisterAPI = OffeneRegisterAPI()

    def verify(self) -> bool:
        return super().verify()

    def finish(self):
        pass

    def load_data(self):
        pass

    def run(self) -> DataFrame:
        tqdm.pandas(desc="Running Search Offeneregister for company related data...")

        self.df[self.added_cols] = self.df.progress_apply(
            lambda lead: pd.Series(
                get_lead_hash_generator().hash_check(
                    lead,
                    self._extract_company_related_data,
                    self.name,
                    self.added_cols,
                    lead,
                )
            ),
            axis=1,
        )
        pass

    def _extract_company_related_data(self, lead):
        last_name = lead["Last Name"]
        first_name = lead["First Name"]
        if last_name is None or first_name is None:
            return pd.Series({f"{col}": None for col in self.added_cols})

        company_name = self.offeneregisterAPI.find_companyName_by_lastName_firstName(
            last_name, first_name
        )
        company_objective = (
            self.offeneregisterAPI.find_companyObjective_by_lastName_firstName(
                last_name, first_name
            )
        )
        (
            company_capital,
            company_capital_currency,
        ) = self.offeneregisterAPI.find_companyCapitals_by_lastName_firstName(
            last_name, first_name
        )
        company_address = (
            self.offeneregisterAPI.find_companyAddress_by_lastName_firstName(
                last_name, first_name
            )
        )

        extracted_features = {
            "company_name": company_name,
            "company_objective": company_objective,
            "company_capital": company_capital,
            "company_capital_currency": company_capital_currency,
            "company_address": company_address,
        }
        return pd.Series(extracted_features)
