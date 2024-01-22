# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Berkay Bozkurt <resitberkaybozkurt@gmail.com>

import pandas as pd
from pandas import DataFrame
from tqdm import tqdm

from bdc.steps.helpers import OffeneRegisterAPI, get_lead_hash_generator
from bdc.steps.step import Step
from logger import get_logger

log = get_logger()


class SearchOffeneRegister(Step):
    """
    This class represents a step in the sales lead qualification process that searches for company-related data
    using the OffeneRegisterAPI.

    Attributes:
        name (str): The name of the step.
        required_cols (list): The list of required columns in the input DataFrame.
        added_cols (list): The list of columns to be added to the input DataFrame.
        offeneregisterAPI (OffeneRegisterAPI): An instance of the OffeneRegisterAPI class.

    Methods:
        verify(): Verifies if the step is ready to run.
        finish(): Performs any necessary cleanup or finalization steps.
        load_data(): Loads any required data for the step.
        run(): Executes the step and returns the modified DataFrame.
        _extract_company_related_data(lead): Extracts company-related data for a given lead.

    """

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
        log.info("Search Offeneregister finished with the summary below:")
        for col in self.added_cols:
            col_perc = self.df[col].notna().sum() / len(self.df[col]) * 100
            log.info(f"Percentage of {col} (of all): {col_perc:.2f}%")

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
        return self.df

    def _extract_company_related_data(self, lead):
        """
        Extracts company-related data for a given lead.

        Args:
            lead (pd.Series): The lead data.

        Returns:
            pd.Series: A Series containing the extracted company-related data.

        """
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
