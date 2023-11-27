# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

import numpy as np

from database.models import Lead
from database.parsers import LeadParser
from evp.predictors import LinearRegressionPredictor, Predictors, RegressionPredictor
from logger import get_logger

log = get_logger()


class EstimatedValuePredictor:
    value_predictor: RegressionPredictor

    def __init__(
        self,
        model_type: Predictors = Predictors.LinearRegression,
        model_path: str = None,
    ) -> None:
        # TODO: should we go back to two models?
        match model_type:
            case Predictors.LinearRegression:
                self.value_predictor = LinearRegressionPredictor(model_path=model_path)
            case default:
                log.error(
                    f"Error: EVP initialized with unsupported model type {model_type}!"
                )

    def train(self, data_path: str) -> None:
        leads = LeadParser.parse_leads_from_csv(data_path)
        X = np.array([lead.to_one_hot_vector() for lead in leads])
        y = np.array([lead.lead_value for lead in leads])
        self.value_predictor.train(X, y)

    def save_models(self, model_path: str = None) -> None:
        self.value_predictor.save(path=model_path)

    def estimate_value(self, lead: Lead) -> float:
        # preprocess lead_data to get feature vector for our ML model
        feature_vector = lead.to_one_hot_vector()
        # use the models to predict required values
        value_prediction = self.value_predictor.predict([feature_vector])
        return value_prediction
