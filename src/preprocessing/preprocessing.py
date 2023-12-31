# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Ahmed Sheta <ahmed.sheta@fau.de>


import os
import sys
from ast import literal_eval

import pandas as pd
from scipy import stats
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import (
    LabelEncoder,
    MinMaxScaler,
    MultiLabelBinarizer,
    StandardScaler,
)

current_dir = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()
parent_dir = os.path.join(current_dir, "..")
file_path = os.path.join(current_dir, "../data/last_snapshot.csv")
data = pd.read_csv(file_path)

sys.path.append(parent_dir)
from logger import get_logger

log = get_logger()


class Preprocessing:
    def __init__(self, df):
        self.preprocessed_df = df.copy()
        self.added_classes = None

        self.numerical_data = [
            "google_places_user_ratings_total",
            "google_places_rating",
            "google_places_confidence",
            "reviews_sentiment_score",
            "review_avg_grammatical_score",
            "review_polarization_score",
            "review_highest_rating_ratio",
            "review_lowest_rating_ratio",
            "review_rating_trend",
        ]

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

    def remove_outliers_zscore(self, column):
        z_scores = stats.zscore(self.preprocessed_df[[column]])
        self.preprocessed_df[column] = self.preprocessed_df[
            (z_scores < 3) & (z_scores > -3)
        ]
        return self.preprocessed_df

    def single_label_encoding(self, column):
        # data is a dataframe column of the desired data for pre-processing
        label_encoder = LabelEncoder()
        data_encoded = label_encoder.fit_transform(
            self.preprocessed_df[column].fillna("").astype(str)
        )
        data_encoded_df = pd.DataFrame(data_encoded)
        # self.preprocessed_df = pd.concat([self.preprocessed_df, data_encoded_df], axis=1)
        self.preprocessed_df[column] = data_encoded_df
        return self.preprocessed_df

    def multiple_label_encoding(self, column):
        # data is a dataframe column of the desired data for pre-processing
        self.preprocessed_df[column].fillna("", inplace=True)
        self.preprocessed_df[column] = self.preprocessed_df[column].apply(
            lambda x: literal_eval(x) if x != "" else []
        )
        mlb = MultiLabelBinarizer()
        encoded_data = mlb.fit_transform(self.preprocessed_df[column])
        self.added_classes = mlb.classes_
        encoded_df = pd.DataFrame(encoded_data, columns=self.added_classes)
        self.preprocessed_df = pd.concat([self.preprocessed_df, encoded_df], axis=1)
        return self.preprocessed_df

    def implement_pipeline(self):
        for data_column in self.numerical_data:
            self.preprocessed_df = self.fill_missing_values(data_column)
            self.preprocessed_df = self.min_max_scaling(data_column)

        for data_column in self.categorical_data:
            if data_column == "google_places_detailed_type":
                continue
            self.preprocessed_df = self.single_label_encoding(data_column)

        self.preprocessed_df = self.multiple_label_encoding(
            "google_places_detailed_type"
        )

        log.info("Preprocessing complete!")
        return self.preprocessed_df

    def save_preprocessed_data(self):
        self.categorical_data.remove("google_places_detailed_type")
        columns_to_save = []
        columns_to_save.extend(self.numerical_data)
        columns_to_save.extend(self.categorical_data)
        columns_to_save.extend(self.added_classes)
        selected_df = self.preprocessed_df[columns_to_save]
        save_path = os.path.join(current_dir, "../data/preprocessed_data.csv")
        selected_df.to_csv(save_path, index=False)
        log.info(f"Preprocessed file saved at {save_path}")


if __name__ == "__main__":
    preprocessor = Preprocessing(data)
    df = preprocessor.implement_pipeline()
    preprocessor.save_preprocessed_data()
