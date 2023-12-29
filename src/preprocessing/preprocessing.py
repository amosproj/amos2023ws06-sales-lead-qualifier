# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Ahmed Sheta <ahmed.sheta@fau.de>

import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

csv_file_path = "src\data\snapshots2023_12_28_232639_regional_atlas_snapshot.csv"

numerical_data = [
    google_places_user_ratings_total,
    google_places_rating,
    google_places_price_level,
    google_places_confidence,
    reviews_sentiment_score,
    review_avg_grammatical_score,
    review_polarization_score,
    review_highest_rating_ratio,
    review_lowest_rating_ratio,
    review_rating_trend,
]

# TODO: google_places_confidence should be incorperated differently somehow, may be as uncertainity

categorical_data = [
    number_country,
    number_area,
    google_places_detailed_type,
    review_polarization_type,
]
