# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

import pytest
from pydantic import ValidationError

from database.models import AnnualIncome, LeadValue, ProductOfInterest
from database.parsers import LeadParser


@pytest.mark.parametrize(
    "create_lead_dict, result",
    [
        ({"lead_id": 0}, 0),
        ({"lead_id": 12999}, 12999),
        ({"lead_id": 40000}, 40000),
        ({"lead_id": 42}, 42),
    ],
    indirect=["create_lead_dict"],
)
def test_lead_id(create_lead_dict, result):
    lead = LeadParser.parse_lead_from_dict(create_lead_dict)
    assert lead.lead_id == result


@pytest.mark.parametrize(
    "create_lead_dict, result",
    [
        ({"first_name": ""}, ""),
        ({"first_name": "Felix"}, "Felix"),
        ({"first_name": '|%$&"\n'}, '|%$&"\n'),
        ({"first_name": "42"}, "42"),
    ],
    indirect=["create_lead_dict"],
)
def test_first_name(create_lead_dict, result):
    lead = LeadParser.parse_lead_from_dict(create_lead_dict)
    assert lead.first_name == result


@pytest.mark.parametrize(
    "create_lead_dict, result",
    [
        ({"last_name": ""}, ""),
        ({"last_name": "Felix"}, "Felix"),
        ({"last_name": '|%$&"\n'}, '|%$&"\n'),
        ({"last_name": "42"}, "42"),
    ],
    indirect=["create_lead_dict"],
)
def test_last_name(create_lead_dict, result):
    lead = LeadParser.parse_lead_from_dict(create_lead_dict)
    assert lead.last_name == result


@pytest.mark.parametrize(
    "create_lead_dict, result, expected_exception",
    [
        ({"email_address": "thisisanemail"}, "", ValidationError),
        ({"email_address": "email@domain.com"}, "email@domain.com", None),
        ({"email_address": "first.last@google.de"}, "first.last@google.de", None),
        ({"email_address": ""}, "", ValidationError),
        ({"email_address": "first.last@domain"}, "", ValidationError),
        ({"email_address": "first.last.com"}, "", ValidationError),
    ],
    indirect=["create_lead_dict"],
)
def test_email_address(create_lead_dict, result, expected_exception):
    if expected_exception:
        with pytest.raises(expected_exception):
            lead = LeadParser.parse_lead_from_dict(create_lead_dict)
    else:
        lead = LeadParser.parse_lead_from_dict(create_lead_dict)
        assert lead.email_address == result


@pytest.mark.parametrize(
    "create_lead_dict, result",
    [
        ({"phone_number": "49123123123"}, "49123123123"),
        ({"phone_number": "31321321321"}, "31321321321"),
        ({"phone_number": ""}, ""),
    ],
    indirect=["create_lead_dict"],
)
def test_phone_number(create_lead_dict, result):
    lead = LeadParser.parse_lead_from_dict(create_lead_dict)
    assert lead.phone_number == result


@pytest.mark.parametrize(
    "create_lead_dict, result",
    [
        ({"annual_income": 0}, AnnualIncome.Nothing),
        ({"annual_income": 12999}, AnnualIncome.Class1),
        ({"annual_income": 40000}, AnnualIncome.Class2),
        ({"annual_income": 75029}, AnnualIncome.Class3),
        ({"annual_income": 144586}, AnnualIncome.Class4),
        ({"annual_income": 200001}, AnnualIncome.Class5),
        ({"annual_income": 599999}, AnnualIncome.Class6),
        ({"annual_income": 1000000}, AnnualIncome.Class7),
        ({"annual_income": 1309481}, AnnualIncome.Class8),
        ({"annual_income": 4921093}, AnnualIncome.Class9),
        ({"annual_income": 10000000}, AnnualIncome.Class10),
    ],
    indirect=["create_lead_dict"],
)
def test_annual_income(create_lead_dict, result):
    lead = LeadParser.parse_lead_from_dict(create_lead_dict)
    assert lead.annual_income == result


@pytest.mark.parametrize(
    "create_lead_dict, result, expected_exception",
    [
        ({"product_of_interest": ""}, "", ValueError),
        ({"product_of_interest": "Nothing"}, ProductOfInterest.Nothing, None),
        ({"product_of_interest": "Terminals"}, ProductOfInterest.Terminals, None),
        (
            {"product_of_interest": "Cash Register System"},
            ProductOfInterest.CashRegisterSystem,
            None,
        ),
        (
            {"product_of_interest": "Business Account"},
            ProductOfInterest.BusinessAccount,
            None,
        ),
        ({"product_of_interest": "All"}, ProductOfInterest.All, None),
        ({"product_of_interest": "Other"}, ProductOfInterest.Other, None),
        ({"product_of_interest": "Bisuness Account"}, "", ValueError),
    ],
    indirect=["create_lead_dict"],
)
def test_product_of_interest(create_lead_dict, result, expected_exception):
    if expected_exception:
        with pytest.raises(expected_exception):
            lead = LeadParser.parse_lead_from_dict(create_lead_dict)
    else:
        lead = LeadParser.parse_lead_from_dict(create_lead_dict)
        assert lead.product_of_interest == result


@pytest.mark.parametrize(
    "create_lead_dict, result, expected_exception",
    [
        ({}, None, None),
        ({"customer_probability": 0.0}, None, None),
        ({"life_time_value": 20000}, None, None),
        (
            {"customer_probability": 0.0, "life_time_value": 20000},
            LeadValue(customer_probability=0.0, life_time_value=20000),
            None,
        ),
        (
            {"customer_probability": 1.0, "life_time_value": 0},
            LeadValue(customer_probability=1.0, life_time_value=0),
            None,
        ),
        ({"customer_probability": 0.5, "life_time_value": -1}, None, ValidationError),
        ({"customer_probability": -0.1, "life_time_value": 42}, None, ValidationError),
        ({"customer_probability": 1.1, "life_time_value": 42}, None, ValidationError),
        (
            {"customer_probability": 0.5, "life_time_value": 0},
            LeadValue(customer_probability=0.5, life_time_value=0),
            None,
        ),
        (
            {"customer_probability": 0.5, "life_time_value": 300},
            LeadValue(customer_probability=0.5, life_time_value=300),
            None,
        ),
    ],
    indirect=["create_lead_dict"],
)
def test_lead_value(create_lead_dict, result, expected_exception):
    if expected_exception:
        with pytest.raises(expected_exception):
            lead = LeadParser.parse_lead_from_dict(create_lead_dict)
    else:
        lead = LeadParser.parse_lead_from_dict(create_lead_dict)
        assert lead.lead_value == result
