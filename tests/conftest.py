# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

import os
import sys
from typing import Dict

import pytest
from mock_components import get_database_mock


@pytest.fixture
def mock_database():
    sys.path.append(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
    )
    import database

    database._database = get_database_mock()
    yield database.get_database()
    database._database = None


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
