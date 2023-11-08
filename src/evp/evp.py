# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

import numpy as np
from sklearn.linear_model import LinearRegression

from database import get_database
from database.models import LeadValue


class EstimatedValuePredictor:
    def __init__(self) -> None:
        self.probability_predictor = LinearRegression()
        self.life_time_value_predictor = LinearRegression()

        all_leads = get_database().get_all_leads()
        X = np.identity(len(all_leads))
        y_probability = np.array(
            [lead.lead_value.customer_probability for lead in all_leads]
        )
        y_value = np.array([lead.lead_value.life_time_value for lead in all_leads])

        self.probability_predictor.fit(X, y_probability)
        self.life_time_value_predictor.fit(X, y_value)

    def estimate_value(self, lead_id) -> LeadValue:
        # make call to data base to retrieve relevant fields for this lead
        lead = get_database().get_lead_by_id(lead_id)

        # preprocess lead_data to get feature vector for our ML model
        feature_vector = np.zeros((1, 5))
        feature_vector[0][lead.lead_id] = 1.0

        # use the models to predict required values
        lead_value_pred = self.life_time_value_predictor.predict(feature_vector)
        # manually applying sigmoid to ensure value in range 0, 1
        cust_prob_pred = 1 / (
            1 + np.exp(-self.probability_predictor.predict(feature_vector))
        )

        lead.lead_value = LeadValue(
            life_time_value=lead_value_pred, customer_probability=cust_prob_pred
        )
        get_database().update_lead(lead)

        # might not need to return here if the database is updated by this function
        return lead.lead_value
