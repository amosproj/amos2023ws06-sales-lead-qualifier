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
sys.path.append(parent_dir)
from database import get_database
from logger import get_logger

log = get_logger()


class Preprocessing:
    def __init__(self, df, filter_null_data=True):
        self.preprocessed_df = df.copy()

        self.filter_bool = filter_null_data
        # columns that would be added later after one-hot encoding each class
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
        # numerical data that need scaling
        self.data_to_scale = ["google_places_user_ratings_total"]

        # categorical data that needs one-hot encoding
        self.categorical_data = [
            "number_country",
            "number_area",
            "google_places_detailed_type",
            "review_polarization_type",
        ]

    def filter_out_null_data(self):
        self.preprocessed_df = self.preprocessed_df[
            self.preprocessed_df["google_places_rating"].notnull()
        ]

    def fill_missing_values(self, column, strategy="constant"):
        if column in self.preprocessed_df.columns:
            imputer = SimpleImputer(strategy=strategy)
            self.preprocessed_df[column] = imputer.fit_transform(
                self.preprocessed_df[[column]]
            )
        else:
            log.info(f"The column '{column}' does not exist in the DataFrame.")

        return self.preprocessed_df

    def standard_scaling(self, column):
        # scales the data in such that the mean of the data becomes 0 and the standard deviation becomes 1.
        if column in self.preprocessed_df.columns:
            scaler = StandardScaler()
            self.preprocessed_df[column] = scaler.fit_transform(
                self.preprocessed_df[[column]]
            )
        return self.preprocessed_df

    def min_max_scaling(self, column):
        # scales the data to a given range, usually between 0 and 1.
        if column in self.preprocessed_df.columns:
            scaler = MinMaxScaler()
            self.preprocessed_df[column] = scaler.fit_transform(
                self.preprocessed_df[[column]]
            )
        return self.preprocessed_df

    def robust_scaling(self, column):
        if column in self.preprocessed_df.columns:
            scaler = RobustScaler()
            self.preprocessed_df[column] = scaler.fit_transform(
                self.preprocessed_df[[column]]
            )
        return self.preprocessed_df

    def normalization(self, column):
        if column in self.preprocessed_df.columns:
            scaler = Normalizer()
            self.preprocessed_df[column] = scaler.fit_transform(
                self.preprocessed_df[[column]]
            )
        return self.preprocessed_df

    def remove_outliers_zscore(self, column):
        THRESHOLD = 3
        z_scores = stats.zscore(self.preprocessed_df[[column]])
        self.preprocessed_df[column] = self.preprocessed_df[
            (z_scores < THRESHOLD) & (z_scores > -1 * THRESHOLD)
        ]
        return self.preprocessed_df

    def single_one_hot_encoding(self, column):
        # one-hot encoding categorical data and creating columns for the newly created classes
        if column in self.preprocessed_df.columns:
            data_to_encode = self.preprocessed_df[[column]].fillna("").astype(str)
            encoder = OneHotEncoder(sparse=False)
            encoded_data = encoder.fit_transform(data_to_encode)
            encoded_columns = encoder.get_feature_names_out([column])
            self.added_classes.extend(encoded_columns)
            encoded_df = pd.DataFrame(
                encoded_data, columns=encoded_columns, index=self.preprocessed_df.index
            )
            self.preprocessed_df = pd.concat([self.preprocessed_df, encoded_df], axis=1)
        else:
            log.info(f"The column '{column}' does not exist in the DataFrame.")

        return self.preprocessed_df

    def multiple_label_encoding(self, column):
        if column in self.preprocessed_df.columns:
            # one-hot encoding for the columns that has multiple labels as element
            self.preprocessed_df[column].fillna("", inplace=True)
            self.preprocessed_df[column] = self.preprocessed_df[column].apply(
                lambda x: literal_eval(x) if x != "" else []
            )
            mlb = MultiLabelBinarizer()
            encoded_data = mlb.fit_transform(self.preprocessed_df[column])
            self.added_classes.extend(mlb.classes_)
            if self.filter_bool:
                encoded_df = pd.DataFrame(
                    encoded_data, columns=mlb.classes_, index=self.preprocessed_df.index
                )
            else:
                encoded_df = pd.DataFrame(encoded_data, columns=mlb.classes_)
            self.preprocessed_df = pd.concat([self.preprocessed_df, encoded_df], axis=1)
        else:
            log.info(f"The column '{column}' does not exist in the DataFrame.")

        return self.preprocessed_df

    def implement_preprocessing_pipeline(self):
        if self.filter_bool:
            self.filter_out_null_data()

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
                    f"Failed to one-hot encode data type ({data_column})! Error: {e}"
                )

        try:
            self.preprocessed_df = self.multiple_label_encoding(
                "google_places_detailed_type"
            )
        except ValueError as e:
            log.error(
                f"Failed to one-hot encode data type 'google_places_detailed_type'! Error: {e}"
            )

        log.info("Preprocessing complete!")
        return self.preprocessed_df

    def save_preprocessed_data(self):
        columns_to_save = []
        columns_to_save.extend(self.numerical_data)
        columns_to_save.extend(self.added_classes)
        selected_df = pd.DataFrame()
        try:
            for column in columns_to_save:
                if column in self.preprocessed_df.columns:
                    selected_df[column] = self.preprocessed_df[column]
        except ValueError as e:
            log.error(f"Failed to save the selected columns for preprocessing! {e}")
        try:
            save_path = os.path.join(current_dir, "../data/preprocessed_data.csv")
            selected_df.to_csv(save_path, index=False)
            log.info(f"Preprocessed data file saved at {save_path}")
        except ValueError as e:
            log.error(f"Failed to save preprocessed data file! {e}")
