# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

from database.models import LeadValue
from evp.evp import EstimatedValuePredictor


def test_estimate_value(mock_database):
    leads = mock_database.get_all_leads()
    evp = EstimatedValuePredictor()
    for lead in leads:
        value = evp.estimate_value(lead.lead_id)
        assert type(value) == LeadValue
