# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

from abc import ABC, abstractmethod
from enum import Enum

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score
from tqdm import tqdm

from database import get_database
from logger import get_logger

log = get_logger()


class Predictors(Enum):
    RandomForest = "Random Forest"


class MerchantSizeByDPV(Enum):
    Invalid = -1
    XS = 0
    S = 1
    M = 2
    L = 3
    XL = 4


class Classifier(ABC):
    @abstractmethod
    def __init__(self, model_name: str = None, *args, **kwargs) -> None:
        self.epochs = "untrained"
        self.f1_test = "untrained"
        self.classification_report = {
            "epochs": self.epochs,
            "weighted avg": {"f1-score": self.f1_test},
        }

    @abstractmethod
    def predict(self, X) -> list[MerchantSizeByDPV]:
        pass

    @abstractmethod
    def train(
        self, X_train, y_train, X_test, y_test, epochs=1, batch_size=None
    ) -> None:
        pass

    @abstractmethod
    def save(self) -> None:
        pass

    @abstractmethod
    def load(self, model_name: str) -> None:
        pass


class RandomForest(Classifier):
    def __init__(
        self,
        model_name: str = None,
        n_estimators=100,
        class_weight=None,
        random_state=42,
    ) -> None:
        super().__init__()
        self.random_state = random_state
        if model_name is not None:
            self.load(model_name)
            if self.model is None:
                self._init_new_model(
                    n_estimators=n_estimators, class_weight=class_weight
                )
        else:
            self._init_new_model(n_estimators=n_estimators, class_weight=class_weight)

    def _init_new_model(self, n_estimators=100, class_weight=None):
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            class_weight=class_weight,
            random_state=self.random_state,
        )

    def predict(self, X) -> MerchantSizeByDPV:
        return self.model.predict(X)

    def train(
        self, X_train, y_train, X_test, y_test, epochs=1, batch_size=None
    ) -> None:
        log.info("Training RandomForestModel")

        self.model.fit(X_train, y_train)

        # inference
        y_pred = self.model.predict(X_test)
        # metrics
        accuracy = accuracy_score(y_test, y_pred)
        f1_test = f1_score(y_test, y_pred, average="weighted")

        log.info(f"F1 Score on Testing Set: {f1_test:.4f}")
        log.info("Computing classification report")
        self.classification_report = classification_report(
            y_test, y_pred, output_dict=True
        )
        self.classification_report["epochs"] = epochs
        self.epochs = epochs
        self.f1_test = f1_test

    def save(self) -> None:
        model_type = type(self).__name__
        try:
            f1_string = f"{self.f1_test:.4f}"
        except:
            f1_string = self.f1_test
        model_name = (
            f"{model_type.lower()}_epochs({self.epochs})_f1({f1_string})_model.pkl"
        )
        get_database().save_ml_model(self.model, model_name)
        get_database().save_classification_report(
            self.classification_report, model_name
        )

    def load(self, model_name: str) -> None:
        self.model = get_database().load_ml_model(model_name)
        self.classification_report = get_database().load_classification_report(
            model_name
        )
        self.epochs = self.classification_report["epochs"]
        self.f1_test = self.classification_report["weighted avg"]["f1-score"]
