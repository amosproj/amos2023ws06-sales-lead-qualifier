# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

from typing import Dict, List

import numpy as np
import pandas as pd

from database.models import (
    AnnualIncome,
    BusinessStatus,
    Lead,
    LeadValue,
    ProductOfInterest,
)


class LeadParser:
    @staticmethod
    def parse_leads_from_csv(path: str) -> List[Lead]:
        try:
            data_df = pd.read_csv(path)
        except FileNotFoundError:
            print(f"Error: could not find {path} while parsing leads")
        leads = [
            data_df.apply(
                lambda row: Lead(
                    lead_id=row.name,
                    first_name=row["First Name"],
                    last_name=row["Last Name"],
                    email_address=str(row["Email"]),
                    phone_number=str(row["Phone"]),
                    annual_income=None,
                    product_of_interest=ProductOfInterest("Other"),
                    lead_value=None,
                    domain=row["domain"] if not pd.isna(row["domain"]) else None,
                    number_valid=row["number_valid"],
                    number_possible=row["number_possible"],
                    google_places_business_status=BusinessStatus(
                        row["google_places_business_status"]
                    )
                    if not pd.isna(row["google_places_business_status"])
                    else None,
                    google_places_user_ratings_total=int(
                        row["google_places_user_ratings_total"]
                    )
                    if not pd.isna(row["google_places_user_ratings_total"])
                    else None,
                ),
                axis=1,
            )
        ]
        print(leads)

    @staticmethod
    def parse_lead_from_dict(data: Dict) -> Lead:
        customer_probability = (
            data["customer_probability"]
            if "customer_probability" in data.keys()
            else None
        )
        life_time_value = (
            data["life_time_value"] if "life_time_value" in data.keys() else None
        )

        if customer_probability is not None and life_time_value is not None:
            lead_value = LeadValue(
                life_time_value=life_time_value,
                customer_probability=customer_probability,
            )
        else:
            lead_value = None

        annual_income = AnnualIncome.Nothing
        for income_value in AnnualIncome:
            if data["annual_income"] < income_value:
                break
            annual_income = income_value

        return Lead(
            lead_id=data["lead_id"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            email_address=data["email_address"],
            phone_number=data["phone_number"],
            annual_income=annual_income,
            product_of_interest=ProductOfInterest(data["product_of_interest"]),
            lead_value=lead_value,
        )
