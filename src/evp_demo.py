# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

from database import get_database
from evp.evp import EstimatedValuePredictor

lead_id = 1

lead = get_database().get_lead_by_id(lead_id)

evp = EstimatedValuePredictor()
lead_value = evp.estimate_value(lead_id)

print(
    f"""
    Dummy prediction for lead#{lead.lead_id}:

    Lead:
    {lead}

    This lead has a predicted probability of {lead_value.customer_probability:.2f} to become a customer.
    This lead has a predicted life time value of {lead_value.life_time_value:.2f}.

    This results in a total lead value of {lead_value.get_lead_value():.2f}.
"""
)
