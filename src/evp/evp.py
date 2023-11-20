# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

import pickle
from typing import List

import numpy as np
from sklearn.linear_model import LinearRegression

from database import get_database
from database.models import Lead, LeadValue

# TODO: create function to make a feature vector from a lead
# TODO: maybe make the predictors their own class?
# TODO: save fully pipelined csv under a different name
# TODO: split into train/val/test
# TODO: train a model and save it


def create_feature_vector(leads: List[Lead]) -> np.ndarray:
    pass


class EstimatedValuePredictor:
    def __init__(
        self,
        model_type: str = "linear_regression",
        prob_path: str = None,
        val_path: str = None,
    ) -> None:
        # TODO: possibly two different models for probability and life time value
        match model_type:
            case "linear_regression":
                try:
                    self.probability_predictor = (
                        LinearRegression()
                        if prob_path is None
                        else pickle.load(open(prob_path, "rb"))
                    )
                    self.life_time_value_predictor = (
                        LinearRegression()
                        if val_path is None
                        else pickle.load(open(val_path, "rb"))
                    )
                except FileNotFoundError:
                    print(
                        f"Error: EVP could not find model at {prob_path} or {val_path}!"
                    )
            case default:
                print(
                    f"Error: EVP initialized with unsupported model type {model_type}!"
                )

    def train(self) -> None:
        all_leads = get_database().get_all_leads()
        self.dimension = len(all_leads)
        X = np.identity(self.dimension)
        y_probability = np.array(
            [lead.lead_value.customer_probability for lead in all_leads]
        )
        y_value = np.array([lead.lead_value.life_time_value for lead in all_leads])

        self.probability_predictor.fit(X, y_probability)
        self.life_time_value_predictor.fit(X, y_value)

    def save_models(self, prob_path: str = None, val_path: str = None) -> None:
        try:
            pickle.dump(self.probability_predictor, open(prob_path, "wb"))
            pickle.dump(self.life_time_value_predictor, open(val_path, "wb"))
        except Exception as e:
            print(f"Error: EVP could not save model at {prob_path} or {val_path}! {e}")

    def estimate_value(self, lead_id) -> LeadValue:
        # make call to data base to retrieve relevant fields for this lead
        lead = get_database().get_lead_by_id(lead_id)

        # preprocess lead_data to get feature vector for our ML model
        feature_vector = np.zeros((1, self.dimension))
        feature_vector[0][lead.lead_id - 1] = 1.0

        # use the models to predict required values
        lead_value_pred = self.life_time_value_predictor.predict(feature_vector)
        # manually applying sigmoid to ensure value in range 0, 1
        cust_prob_pred = 1 / (
            1 + np.exp(-self.probability_predictor.predict(feature_vector))
        )

        lead.lead_value = LeadValue(
            life_time_value=lead_value_pred, customer_probability=cust_prob_pred
        )
        # get_database().update_lead(lead)

        # might not need to return here if the database is updated by this function
        return lead.lead_value
