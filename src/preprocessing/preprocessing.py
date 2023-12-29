# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Ahmed Sheta <ahmed.sheta@fau.de>


import os
from ast import literal_eval

import pandas as pd
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer, StandardScaler

csv_file_path = "../data/last_snapshot.csv"
current_dir = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()
file_path = os.path.join(current_dir, "../data/last_snapshot.csv")
data = pd.read_csv(file_path)

numerical_data = [
    "google_places_user_ratings_total",
    "google_places_rating",
    "google_places_price_level",
    "google_places_confidence",
    "reviews_sentiment_score",
    "review_avg_grammatical_score",
    "review_polarization_score",
    "review_highest_rating_ratio",
    "review_lowest_rating_ratio",
    "review_rating_trend",
]

# TODO: google_places_confidence should be incorperated differently somehow, may be as uncertainity

categorical_data = [
    "number_country",
    "number_area",
    "google_places_detailed_type",
    "review_polarization_type",
]

#################### encode the google_places_detailed_type data ####################

detailed_type = data["google_places_detailed_type"]
detailed_type.fillna("", inplace=True)
detailed_type = detailed_type.apply(lambda x: literal_eval(x) if x != "" else [])

mlb = MultiLabelBinarizer()
encoded_detailed_type = mlb.fit_transform(detailed_type)
encoded_detailed_type_df = pd.DataFrame(encoded_detailed_type, columns=mlb.classes_)

# print(f"encoded_detailed_type = {encoded_detailed_type}")
# print(f"encoded_detailed_type_df = {encoded_detailed_type_df}")

########################## encode country name data #################################

country_name = data["number_area"]
country_name.fillna("", inplace=True)
country_encoder = LabelEncoder()
data["country_encoded"] = country_encoder.fit_transform(country_name)

# print(f"data['Country_LabelEncoded'] = {data['Country_LabelEncoded']}")

########################## encode area name data ####################################

area_name = data["number_country"]
area_name.fillna("", inplace=True)
area_encoder = LabelEncoder()
data["area_encoded"] = area_encoder.fit_transform(area_name)

# print(f"data['area_encoded'] = {data['area_encoded']}")

######################### encode review_polarization_type data ######################

polarization_type = data["review_polarization_type"]
polarization_type.fillna("", inplace=True)
polarization_encoder = LabelEncoder()
data["review_polarization_type"] = polarization_encoder.fit_transform(polarization_type)

print(f"data['review_polarization_type'] = {data['review_polarization_type']}")
