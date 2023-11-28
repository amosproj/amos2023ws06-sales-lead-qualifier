# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

from typing import Dict, List

import numpy as np
import pandas as pd

from database.models import (
    AnnualIncome,
    BusinessStatus,
    Lead,
    ProductOfInterest,
    UserRatingsTotal,
)
from logger import get_logger

log = get_logger()


class LeadParser:
    @staticmethod
    def parse_leads_from_csv(path: str) -> List[Lead]:
        try:
            data_df = pd.read_csv(path)
        except FileNotFoundError:
            log.error(f"Could not find {path} while parsing leads")
        leads = data_df.apply(
            lambda row: Lead(
                lead_id=row.name,
                first_name=row["First Name"],
                last_name=row["Last Name"],
                email_address=str(row["Email"]),
                phone_number=str(row["Phone"]),
                annual_income=AnnualIncome.Undefined,
                product_of_interest=ProductOfInterest.Undefined,
                lead_value=float(row["lead_value"]) if "lead_value" in row else None,
                domain=row["domain"] if not pd.isna(row["domain"]) else None,
                number_valid=row["number_valid"],
                number_possible=row["number_possible"],
                google_places_business_status=BusinessStatus(
                    row["google_places_business_status"]
                ),
                google_places_user_ratings_total=UserRatingsTotal(
                    row["google_places_user_ratings_total"]
                ),
            ),
            axis=1,
        ).to_list()
        return leads

    @staticmethod
    def parse_lead_from_dict(data: Dict) -> Lead:
        print(data)
        return Lead(
            lead_id=data["lead_id"],
            first_name=data["First Name"],
            last_name=data["Last Name"],
            email_address=str(data["Email"]),
            phone_number=str(data["Phone"]),
            annual_income=AnnualIncome.Undefined,
            product_of_interest=ProductOfInterest.Undefined,
            lead_value=float(data["lead_value"]) if "lead_value" in data else None,
            domain=data["domain"] if not pd.isna(data["domain"]) else None,
            number_valid=data["number_valid"],
            number_possible=data["number_possible"],
            google_places_business_status=BusinessStatus(
                data["google_places_business_status"]
            ),
            google_places_user_ratings_total=UserRatingsTotal(
                data["google_places_user_ratings_total"]
            ),
        )
