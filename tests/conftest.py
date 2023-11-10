# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

from typing import Dict

import pytest


@pytest.fixture
def create_lead_dict(request) -> Dict:
    lead_value_adjustments = request.param
    lead_data = {
        "lead_id": 0,
        "annual_income": 0,
        "product_of_interest": "Nothing",
        "first_name": "Manu",
        "last_name": "Musterperson",
        "phone_number": "49123123123",
        "email_address": "test@test.de",
    }
    for key, value in lead_value_adjustments.items():
        lead_data[key] = value
    yield lead_data
