# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from database import get_database
from database.models import LeadValue
from evp.evp import EstimatedValuePredictor


def test_estimate_value():
    leads = get_database().get_all_leads()
    evp = EstimatedValuePredictor()
    for lead in leads:
        value = evp.estimate_value(lead.lead_id)
        assert type(value) == LeadValue
