# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

from abc import ABC, abstractmethod
from enum import Enum

import lightgbm as lgb
import xgboost as xgb
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.naive_bayes import BernoulliNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

from database import get_database
from logger import get_logger

log = get_logger()


class Predictors(Enum):
    RandomForest = "Random Forest"
    XGBoost = "XGBoost"
    NaiveBayes = "Naive Bayes"
    KNN = "KNN Classifier"
    AdaBoost = "AdaBoost"
    LightGBM = "LightGBM"


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
    def _init_new_model(self):
        pass

    @abstractmethod
    def predict(self, X) -> list[MerchantSizeByDPV]:
        pass

    @abstractmethod
    def train(
        self, X_train, y_train, X_test, y_test, epochs=1, batch_size=None
    ) -> None:
        log.info(f"Training {type(self).__name__} for {epochs} epochs")

        self.model.fit(X_train, y_train)

        y_pred = self.model.predict(X_test)
        f1_test = f1_score(y_test, y_pred, average="weighted")
        log.info(f"F1 Score on Testing Set: {f1_test:.4f}")
        log.info("Computing classification report")
        self.classification_report = classification_report(
            y_test, y_pred, output_dict=True
        )
        self.classification_report["epochs"] = epochs
        self.epochs = epochs
        self.f1_test = f1_test

    def save(self, num_classes: int = 5) -> None:
        model_type = type(self).__name__
        try:
            f1_string = f"{self.f1_test:.4f}"
        except:
            f1_string = self.f1_test
        model_name = f"{model_type.lower()}_epochs({self.epochs})_f1({f1_string})_numclasses({num_classes})_model.pkl"
        get_database().save_ml_model(self.model, model_name)
        get_database().save_classification_report(
            self.classification_report, model_name
        )

    def load(self, model_name: str) -> None:
        loaded_model = get_database().load_ml_model(model_name)
        loaded_classification_report = get_database().load_classification_report(
            model_name
        )
        if loaded_model is not None:
            self.model = loaded_model
        if loaded_classification_report is not None:
            self.classification_report = loaded_classification_report
        self.epochs = self.classification_report["epochs"]
        self.f1_test = self.classification_report["weighted avg"]["f1-score"]


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
        self.model = None
        if model_name is not None:
            self.load(model_name)
            if self.model is None:
                log.info(
                    f"Loading model '{model_name}' failed. Initializing new untrained model!"
                )
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
        super().train(
            X_train, y_train, X_test, y_test, epochs=epochs, batch_size=batch_size
        )


class NaiveBayesClassifier(Classifier):
    def __init__(self, model_name: str = None, random_state=42) -> None:
        super().__init__()
        self.random_state = random_state
        self.model = None
        if model_name is not None:
            self.load(model_name)
            if self.model is None:
                log.info(
                    f"Loading model '{model_name}' failed. Initializing new untrained model!"
                )
                self._init_new_model()
        else:
            self._init_new_model()

    def _init_new_model(self):
        self.model = BernoulliNB()

    def predict(self, X) -> list[MerchantSizeByDPV]:
        return self.model.predict(X)

    def train(
        self, X_train, y_train, X_test, y_test, epochs=1, batch_size=None
    ) -> None:
        super().train(
            X_train, y_train, X_test, y_test, epochs=epochs, batch_size=batch_size
        )


class KNNClassifier(Classifier):
    def __init__(
        self,
        model_name: str = None,
        random_state=42,
        n_neighbors=10,
        weights="distance",
    ) -> None:
        super().__init__()
        self.random_state = random_state
        self.n_neighbors = n_neighbors
        self.weights = weights
        self.model = None
        if model_name is not None:
            self.load(model_name)
            if self.model is None:
                log.info(
                    f"Loading model '{model_name}' failed. Initializing new untrained model!"
                )
                self._init_new_model()
        else:
            self._init_new_model()

    def _init_new_model(self):
        self.model = KNeighborsClassifier(
            n_neighbors=self.n_neighbors, weights=self.weights
        )

    def predict(self, X) -> list[MerchantSizeByDPV]:
        return self.model.predict(X)

    def train(
        self, X_train, y_train, X_test, y_test, epochs=1, batch_size=None
    ) -> None:
        super().train(
            X_train, y_train, X_test, y_test, epochs=epochs, batch_size=batch_size
        )


class XGB(Classifier):
    def __init__(
        self,
        model_name: str = None,
        num_rounds=2000,
        random_state=42,
    ) -> None:
        super().__init__()
        self.random_state = random_state
        self.model = None
        self.num_rounds = num_rounds
        if model_name is not None:
            self.load(model_name)
            if self.model is None:
                log.info(
                    f"Loading model '{model_name}' failed. Initializing new untrained model!"
                )
                self._init_new_model(num_rounds == num_rounds)
        else:
            self._init_new_model(num_rounds == num_rounds)

    def _init_new_model(self, num_rounds=1000):
        self.params = {
            "objective": "multi:softmax",
            "num_class": 5,
            "max_depth": 3,
            "learning_rate": 0.1,
            "eval_metric": "mlogloss",
        }

    def predict(self, X) -> MerchantSizeByDPV:
        return self.model.predict(X)

    def train(
        self, X_train, y_train, X_test, y_test, epochs=1, batch_size=None
    ) -> None:
        log.info("Training XGBoost")

        dtrain = xgb.DMatrix(X_train, label=y_train)
        dtest = xgb.DMatrix(X_test, label=y_test)
        self.model = xgb.train(self.params, dtrain, self.num_rounds)

        # inference
        y_pred = self.model.predict(dtest)
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


class AdaBoost(Classifier):
    def __init__(
        self,
        model_name: str = None,
        n_estimators=100,
        class_weight=None,
        random_state=42,
    ) -> None:
        super().__init__()
        self.random_state = random_state
        self.model = None
        if model_name is not None:
            self.load(model_name)
            if self.model is None:
                log.info(
                    f"Loading model '{model_name}' failed. Initializing new untrained model!"
                )
                self._init_new_model(
                    n_estimators=n_estimators, class_weight=class_weight
                )
        else:
            self._init_new_model(n_estimators=n_estimators, class_weight=class_weight)

    def _init_new_model(self, n_estimators=100, class_weight=None):
        self.model = AdaBoostClassifier(
            estimator=DecisionTreeClassifier(max_depth=None, class_weight=class_weight),
            n_estimators=n_estimators,
            random_state=self.random_state,
        )

    def predict(self, X) -> MerchantSizeByDPV:
        return self.model.predict(X)

    def train(
        self, X_train, y_train, X_test, y_test, epochs=1, batch_size=None
    ) -> None:
        super().train(
            X_train, y_train, X_test, y_test, epochs=epochs, batch_size=batch_size
        )

        
class LightGBM(Classifier):
    def __init__(
        self,
        model_name: str = None,
        num_leaves=2000,
        random_state=42,
    ) -> None:
        super().__init__()
        self.random_state = random_state
        self.model = None
        self.num_leaves = num_leaves
        if model_name is not None:
            self.load(model_name)
            if self.model is None:
                log.info(
                    f"Loading model '{model_name}' failed. Initializing new untrained model!"
                )
                self._init_new_model(num_leaves == num_leaves)
        else:
            self._init_new_model(num_leaves == num_leaves)

    def _init_new_model(self, num_rounds=1000):
        self.params_lgb = {
            "boosting_type": "gbdt",
            "objective": "multiclass",
            "metric": "multi_logloss",
            "num_class": 5,
            "num_leaves": self.num_leaves,
            "max_depth": -1,
            "learning_rate": 0.05,
            "feature_fraction": 0.9,
        }
        self.model = lgb.LGBMClassifier(**self.params_lgb)

    def predict(self, X) -> MerchantSizeByDPV:
        return self.model.predict(X)

    def train(
        self, X_train, y_train, X_test, y_test, epochs=1, batch_size=None
    ) -> None:
        log.info("Training LightGBM")

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
