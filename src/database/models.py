# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

from enum import Enum, IntEnum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class AnnualIncome(IntEnum):
    Nothing = 0  # 0€
    Class1 = 1  # (0€, 35000€]
    Class2 = 35001  # (35000€, 60000€]
    Class3 = 60001  # (60000€, 100000€]
    Class4 = 100001  # (100000€, 200000€]
    Class5 = 200001  # (200000€, 400000€]
    Class6 = 400001  # (400000€, 600000€]
    Class7 = 600001  # (600000€, 1000000€]
    Class8 = 1000001  # (1000000€, 2000000€]
    Class9 = 2000001  # (2000000€, 5000000€]
    Class10 = 5000001  # (5000000€, inf€]


class ProductOfInterest(str, Enum):
    Nothing = "Nothing"
    Terminals = "Terminals"
    CashRegisterSystem = "Cash Register System"
    BusinessAccount = "Business Account"
    All = "All"
    Other = "Other"


class LeadValue(BaseModel):
    life_time_value: float
    customer_probability: float = Field(..., ge=0, le=1)

    def get_lead_value(self) -> float:
        return self.life_time_value * self.customer_probability


class Lead(BaseModel):
    lead_id: int  # could be expended to a UUID later
    first_name: str
    last_name: str
    email_address: EmailStr
    phone_number: str
    annual_income: AnnualIncome
    product_of_interest: ProductOfInterest
    lead_value: Optional[LeadValue]
