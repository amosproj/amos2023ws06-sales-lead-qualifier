# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

import numpy as np
from sklearn.linear_model import LinearRegression

from database import get_database


class LeadValue:
    def __init__(
        self, lifetime_value: float = 0, customer_probability: float = 0
    ) -> None:
        assert (
            0.0 <= customer_probability <= 1.0
        ), "Probability of becoming a customer must be between 0.0 and 1.0"
        self.life_time_value = lifetime_value
        self.customer_probability = customer_probability

    def get_lead_value(self) -> float:
        return self.life_time_value * self.customer_probability


class EstimatedValuePredictor:
    def __init__(self) -> None:
        self.probability_predictor = LinearRegression()
        self.life_time_value_predictor = LinearRegression()

        data = get_database().get_all_entries()
        X = np.random.random((len(data), len(data)))
        y_probability = np.array(
            [item["customer_probability"] for item in data.values()]
        )
        y_value = np.array([item["customer_probability"] for item in data.values()])

        self.probability_predictor.fit(X, y_probability)
        self.life_time_value_predictor.fit(X, y_value)

    def estimate_value(self, lead_id) -> LeadValue:
        # make call to data base to retrieve relevant fields for this lead
        lead_data = get_database().get_entry_by_id(lead_id)

        # preprocess lead_data to get feature vector for our ML model
        feature_vector = np.random.random((1, 5))

        # use the models to predict required values
        lead_value_pred = self.life_time_value_predictor.predict(feature_vector)
        # manually applying sigmoid to ensure value in range 0, 1
        cust_prob_pred = 1 / (
            1 + np.exp(-self.probability_predictor.predict(feature_vector))
        )

        return LeadValue(lead_value_pred, cust_prob_pred)
