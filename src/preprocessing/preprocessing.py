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

sys.path.append(current_dir)
log = get_logger()


class Preprocessing:
    def __init__(self, filter_null_data=True, historical_data=False):
        data_repo = get_database()
        self.data_path = data_repo.get_output_path()
        if historical_data:
            input_path_components = self.data_path.split(
                "\\" if "\\" in self.data_path else "/"
            )
            input_path_components.pop()
            input_path_components.pop()
            input_path_components.append("historical_data/100k_historic_enriched.csv")
            input_path = "/".join(input_path_components)
            data = pd.read_csv(input_path)
            log.debug(f"Data path = {input_path}")
        else:
            log.debug(f"Data path = {self.data_path}")
            data = pd.read_csv(self.data_path)
            self.preprocessed_df = data.copy()

        if historical_data:
            self.prerocessed_data_output_path = "s3://amos--data--features/preprocessed_data_files/preprocessed_data.csv"
        else:
            # created the new output path based on which repo used
            path_components = self.data_path.split(
                "\\" if "\\" in self.data_path else "/"
            )
            path_components.pop()
            path_components.append("preprocessed_data.csv")
            self.prerocessed_data_output_path = "/".join(path_components)

        self.filter_bool = filter_null_data
        # columns that would be added later after one-hot encoding each class
        self.added_features = []
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
            "regional_atlas_pop_density",
            "regional_atlas_pop_development",
            "regional_atlas_age_0",
            "regional_atlas_age_1",
            "regional_atlas_age_2",
            "regional_atlas_age_3",
            "regional_atlas_age_4",
            "regional_atlas_pop_avg_age",
            "regional_atlas_per_service_sector",
            "regional_atlas_per_trade",
            "regional_atlas_employment_rate",
            "regional_atlas_unemployment_rate",
            "regional_atlas_per_long_term_unemployment",
            "regional_atlas_investments_p_employee",
            "regional_atlas_gross_salary_p_employee",
            "regional_atlas_disp_income_p_inhabitant",
            "regional_atlas_tot_income_p_taxpayer",
            "regional_atlas_gdp_p_employee",
            "regional_atlas_gdp_development",
            "regional_atlas_gdp_p_inhabitant",
            "regional_atlas_gdp_p_workhours",
            "regional_atlas_pop_avg_age_zensus",
            "regional_atlas_regional_score",
        ]
        # numerical data that need scaling
        self.data_to_scale = []

        # categorical data that needs one-hot encoding
        self.categorical_data = [
            # "number_country",
            # "number_area",
            "google_places_detailed_type",
            "review_polarization_type",
        ]

        self.class_labels = "MerchantSizeByDPV"

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

    def class_label_encoding(self, column):
        size_mapping = {"XS": 0, "S": 1, "M": 2, "L": 3, "XL": 4}
        if column in self.preprocessed_df.columns:
            self.preprocessed_df[column] = self.preprocessed_df[column].map(
                size_mapping
            )
        else:
            log.info(f"Class labels {column} does not exist in the dataframe!")
        return self.preprocessed_df

    def single_one_hot_encoding(self, column):
        # one-hot encoding categorical data and creating columns for the newly created classes
        if column in self.preprocessed_df.columns:
            data_to_encode = self.preprocessed_df[[column]].fillna("").astype(str)
            encoder = OneHotEncoder(sparse=False)
            encoded_data = encoder.fit_transform(data_to_encode)
            encoded_columns = encoder.get_feature_names_out([column])
            self.added_features.extend(encoded_columns)
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
            self.added_features.extend(mlb.classes_)
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

        try:
            self.preprocessed_df = self.class_label_encoding(self.class_labels)
        except ValueError as e:
            log.error(f"Failed to label the classes '{self.class_labels}'! Error: {e}")

        log.info("Preprocessing complete!")

        return self.preprocessed_df

    def save_preprocessed_data(self):
        columns_to_save = []
        columns_to_save.extend(self.numerical_data)
        columns_to_save.extend(self.added_features)
        columns_to_save.append(self.class_labels)
        selected_df = pd.DataFrame()
        try:
            for column in columns_to_save:
                if column in self.preprocessed_df.columns:
                    selected_df[column] = self.preprocessed_df[column]
        except ValueError as e:
            log.error(f"Failed to save the selected columns for preprocessing! {e}")
        try:
            selected_df.to_csv(self.prerocessed_data_output_path, index=False)
            log.info(
                f"Preprocessed dataframe of shape {self.preprocessed_df.shape} is saved at {self.prerocessed_data_output_path}"
            )
        except ValueError as e:
            log.error(f"Failed to save preprocessed data file! {e}")
