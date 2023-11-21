# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

from enum import Enum, IntEnum
from typing import Optional

import numpy as np
from pydantic import BaseModel, EmailStr, Field
from sklearn.preprocessing import OneHotEncoder


class AnnualIncome(IntEnum):
    Undefined = 0  # 0€
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

    @classmethod
    def _missing_(cls, value):
        annual_income = cls.Undefined
        for income_value in cls:
            if value < income_value:
                break
            annual_income = income_value
        return annual_income


class UserRatingsTotal(IntEnum):
    Undefined = 0
    Class1 = 50
    Class2 = 100
    Class3 = 500
    Class4 = 1000
    Class5 = 10000

    @classmethod
    def _missing_(cls, value):
        rating_total = cls.Undefined
        for income_value in cls:
            if value < income_value:
                break
            rating_total = income_value
        return rating_total


class ProductOfInterest(str, Enum):
    Undefined = "Undefined"
    Nothing = "Nothing"
    Terminals = "Terminals"
    CashRegisterSystem = "Cash Register System"
    BusinessAccount = "Business Account"
    All = "All"
    Other = "Other"

    @classmethod
    def _missing_(cls, value):
        return cls.Undefined


class BusinessStatus(str, Enum):
    Undefined = "Undefined"
    Operational = "OPERATIONAL"
    ClosedTemporarily = "CLOSED_TEMPORARILY"
    ClosedPermanently = "CLOSED_PERMANENTLY"

    @classmethod
    def _missing_(cls, value):
        return cls.Undefined


def encode_category(value, categories):
    ohe = OneHotEncoder(sparse_output=False)
    ohe.fit(np.array(categories).reshape(-1, 1))
    encoded = ohe.transform(np.array([value]).reshape(-1, 1))
    return encoded


class Lead(BaseModel):
    lead_id: int  # could be expended to a UUID later
    first_name: str
    last_name: str
    email_address: str
    phone_number: str
    annual_income: Optional[AnnualIncome]
    product_of_interest: Optional[ProductOfInterest]
    lead_value: Optional[float]
    domain: Optional[str]
    number_valid: Optional[bool]
    number_possible: Optional[bool]
    google_places_business_status: Optional[BusinessStatus]
    google_places_user_ratings_total: Optional[UserRatingsTotal]

    def to_one_hot_vector(self):
        vector = np.array([])
        vector = np.append(
            vector,
            encode_category(
                self.annual_income.value, [item.value for item in AnnualIncome]
            ),
        )
        vector = np.append(
            vector,
            encode_category(
                self.product_of_interest.value,
                [item.value for item in ProductOfInterest],
            ),
        )
        vector = np.append(
            vector, np.array([int(self.domain is not None)]).astype(float)
        )
        vector = np.append(
            vector,
            np.array([int(self.number_valid and self.number_possible)]).astype(float),
        )
        vector = np.append(
            vector,
            encode_category(
                self.google_places_business_status.value,
                [item.value for item in BusinessStatus],
            ),
        )
        return vector
