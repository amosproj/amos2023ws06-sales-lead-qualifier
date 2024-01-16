# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.utils import class_weight, resample

from database.models import Lead
from evp.predictors import Classifier, MerchantSizeByDPV, Predictors, RandomForest
from logger import get_logger

log = get_logger()


SEED = 42


class EstimatedValuePredictor:
    lead_classifier: Classifier

    def __init__(
        self,
        data: pd.DataFrame,
        train_size=0.8,
        val_size=0.1,
        test_size=0.1,
        model_type: Predictors = Predictors.RandomForest,
        model_name: str = None,
        **model_args,
    ) -> None:
        self.df = data
        features = self.df.drop("MerchantSizeByDPV", axis=1).to_numpy()
        self.class_labels = self.df["MerchantSizeByDPV"].to_numpy()
        # split the data into training (80%), validation (10%), and testing (10%) sets
        self.X_train, X_temp, self.y_train, y_temp = train_test_split(
            features, self.class_labels, test_size=val_size + test_size, random_state=42
        )
        self.X_val, self.X_test, self.y_val, self.y_test = train_test_split(
            X_temp, y_temp, test_size=val_size / (val_size + test_size), random_state=42
        )

        # Class weights to tackle the class imbalance
        class_weights = class_weight.compute_class_weight(
            "balanced", classes=np.unique(self.y_train), y=self.y_train
        )
        self.class_weight_dict = dict(zip(np.unique(self.y_train), class_weights))

        match model_type:
            case Predictors.RandomForest:
                self.lead_classifier = RandomForest(
                    model_name=model_name,
                    class_weight=self.class_weight_dict,
                    **model_args,
                )
            case default:
                log.error(
                    f"Error: EVP initialized with unsupported model type {model_type}!"
                )

    def train(self, epochs=1, batch_size=None) -> None:
        self.lead_classifier.train(
            self.X_train,
            self.y_train,
            self.X_test,
            self.y_test,
            epochs=epochs,
            batch_size=batch_size,
        )

    def save_model(self) -> None:
        self.lead_classifier.save()

    def predict(self, X) -> list[MerchantSizeByDPV]:
        # use the models to predict required values
        if (
            self.lead_classifier.classification_report["epochs"] == "untrained"
            or self.lead_classifier.classification_report["weighted avg"]["f1-score"]
            == "untrained"
        ):
            log.error("Cannot make predictions with untrained model!")
            return [MerchantSizeByDPV.Invalid]
        merchant_size = self.lead_classifier.predict(X)
        return merchant_size
