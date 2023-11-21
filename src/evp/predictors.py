# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

import pickle
from abc import ABC, abstractmethod
from enum import Enum

from sklearn.linear_model import LinearRegression


class Predictors(Enum):
    LinearRegression = "Linear Regression"


class RegressionPredictor(ABC):
    @abstractmethod
    def __init__(self, model_path: str = None) -> None:
        pass

    @abstractmethod
    def predict(self, X) -> float:
        pass

    @abstractmethod
    def train(self, X, y) -> None:
        pass

    @abstractmethod
    def save(self, path: str) -> None:
        pass

    @abstractmethod
    def load(self, path: str) -> None:
        pass


class LinearRegressionPredictor(RegressionPredictor):
    def __init__(self, model_path: str = None) -> None:
        if model_path is None:
            self.predictor = LinearRegression()
        else:
            try:
                self.predictor = pickle.load(open(model_path, "rb"))
            except FileNotFoundError:
                print(f"Error: Could not find model at {model_path}!")

    def predict(self, X) -> float:
        return self.predictor.predict(X)

    def train(self, X, y) -> None:
        return self.predictor.fit(X, y)

    def save(self, path: str) -> None:
        try:
            pickle.dump(self.predictor, open(path, "wb"))
        except Exception as e:
            print(f"Error: Could not save model at {path}! Exception: {e}")

    def load(self, path: str) -> None:
        try:
            self.predictor = pickle.load(open(path, "rb"))
        except FileNotFoundError:
            print(f"Error: Could not find model at {path}!")
