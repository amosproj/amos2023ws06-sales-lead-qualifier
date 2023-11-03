# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

from typing import Dict

from database.models import AnnualIncome, Lead, LeadValue, ProductOfInterest


class LeadParser:
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
