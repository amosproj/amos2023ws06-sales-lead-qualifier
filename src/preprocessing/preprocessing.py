# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Ahmed Sheta <ahmed.sheta@fau.de>


import os
import sys
from ast import literal_eval

import pandas as pd
from scipy import stats
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import (
    MinMaxScaler,
    MultiLabelBinarizer,
    Normalizer,
    OneHotEncoder,
    RobustScaler,
    StandardScaler,
)

current_dir = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()
parent_dir = os.path.join(current_dir, "..")
file_path = os.path.join(current_dir, "../data/last_snapshot.csv")

sys.path.append(parent_dir)
from logger import get_logger

log = get_logger()


class Preprocessing:
    def __init__(self, df):
        self.preprocessed_df = df.copy()
        self.added_classes = []
        self.numerical_data = [
            "google_places_rating",
            "google_places_user_ratings_total",
            "google_places_confidence",
            "reviews_sentiment_score",
            "review_avg_grammatical_score",
            "review_polarization_score",
            "review_highest_rating_ratio",
            "review_lowest_rating_ratio",
            "review_rating_trend",
        ]

        self.data_to_scale = ["google_places_user_ratings_total"]

        self.categorical_data = [
            "number_country",
            "number_area",
            "google_places_detailed_type",
            "review_polarization_type",
        ]

    def fill_missing_values(self, column, strategy="most_frequent"):
        imputer = SimpleImputer(strategy=strategy)
        self.preprocessed_df[column] = imputer.fit_transform(
            self.preprocessed_df[[column]]
        )
        return self.preprocessed_df

    def standard_scaling(self, column):
        scaler = StandardScaler()
        self.preprocessed_df[column] = scaler.fit_transform(
            self.preprocessed_df[[column]]
        )
        return self.preprocessed_df

    def min_max_scaling(self, column):
        scaler = MinMaxScaler()
        self.preprocessed_df[column] = scaler.fit_transform(
            self.preprocessed_df[[column]]
        )
        return self.preprocessed_df

    def robust_scaling(self, column):
        scaler = RobustScaler()
        self.preprocessed_df[column] = scaler.fit_transform(
            self.preprocessed_df[[column]]
        )
        return self.preprocessed_df

    def normalization(self, column):
        scaler = Normalizer()
        self.preprocessed_df[column] = scaler.fit_transform(
            self.preprocessed_df[[column]]
        )
        return self.preprocessed_df

    def remove_outliers_zscore(self, column):
        z_scores = stats.zscore(self.preprocessed_df[[column]])
        self.preprocessed_df[column] = self.preprocessed_df[
            (z_scores < 3) & (z_scores > -3)
        ]
        return self.preprocessed_df

    def single_one_hot_encoding(self, column):
        data_to_encode = self.preprocessed_df[[column]].fillna("").astype(str)
        encoder = OneHotEncoder(sparse=False)
        encoded_data = encoder.fit_transform(data_to_encode)
        encoded_columns = encoder.get_feature_names_out([column])
        self.added_classes.extend(encoded_columns)
        encoded_df = pd.DataFrame(
            encoded_data, columns=encoded_columns, index=self.preprocessed_df.index
        )
        self.preprocessed_df = pd.concat([self.preprocessed_df, encoded_df], axis=1)

        return self.preprocessed_df

    def multiple_label_encoding(self, column):
        # data is a dataframe column of the desired data for pre-processing
        self.preprocessed_df[column].fillna("", inplace=True)
        self.preprocessed_df[column] = self.preprocessed_df[column].apply(
            lambda x: literal_eval(x) if x != "" else []
        )
        mlb = MultiLabelBinarizer()
        encoded_data = mlb.fit_transform(self.preprocessed_df[column])
        self.added_classes.extend(mlb.classes_)
        encoded_df = pd.DataFrame(encoded_data, columns=mlb.classes_)
        self.preprocessed_df = pd.concat([self.preprocessed_df, encoded_df], axis=1)
        return self.preprocessed_df

    def implement_pipeline(self):
        for data_column in self.numerical_data:
            self.preprocessed_df = self.fill_missing_values(data_column)
            if data_column in self.data_to_scale:
                self.preprocessed_df = self.robust_scaling(data_column)

        for data_column in self.categorical_data:
            if data_column == "google_places_detailed_type":
                continue
            try:
                self.preprocessed_df = self.single_one_hot_encoding(data_column)
            except ValueError as e:
                log.error(
                    f"Failed to hot-one encode data type ({data_column})! Error: {e}"
                )

        try:
            self.preprocessed_df = self.multiple_label_encoding(
                "google_places_detailed_type"
            )
        except ValueError as e:
            log.error(
                f"Failed to hot-one encode data type 'google_places_detailed_type'! Error: {e}"
            )

        log.info("Preprocessing complete!")
        return self.preprocessed_df

    def save_preprocessed_data(self):
        columns_to_save = []
        columns_to_save.extend(self.numerical_data)
        columns_to_save.extend(self.added_classes)

        selected_df = self.preprocessed_df[columns_to_save]
        try:
            save_path = os.path.join(current_dir, "../data/preprocessed_data.csv")
            selected_df.to_csv(save_path, index=False)
            log.info(f"Preprocessed file saved at {save_path}")
        except ValueError as e:
            log.error(f"Failed to save preprocessed file! Error: {e}")


if __name__ == "__main__":
    data = pd.read_csv(file_path)
    preprocessor = Preprocessing(data)
    df = preprocessor.implement_pipeline()
    preprocessor.save_preprocessed_data()
