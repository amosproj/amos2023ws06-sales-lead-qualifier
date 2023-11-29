# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Berkay Bozkurt <resitberkaybozkurt@gmail.com>
# SPDX-FileCopyrightText: 2023 Sophie Heasman <sophieheasmann@gmail.com>
import json
import os.path
from collections import Counter

import language_tool_python as ltp
import numpy as np
import pandas as pd
from pandas import DataFrame
from requests import RequestException
from sklearn.linear_model import LinearRegression
from tqdm import tqdm

from bdc.steps.step import Step, StepError
from config import GOOGLE_PLACES_API_KEY, OPEN_AI_API_KEY
from logger import get_logger

log = get_logger()


class SmartReviewInsightsEnhancer(Step):
    NAME = "Smart-Review-Insights-Enhancer"

    REQUIRED_FIELDS = {"reviews_path": "google_places_detailed_reviews_path"}

    added_cols = [
        "review_avg_grammatical_score",
        "review_polarization_type",
        "review_polarization_score",
        "review_highest_rating_ratio",
        "review_lowest_rating_ratio",
        "review_rating_trend",
    ]
    MIN_RATINGS_COUNT = 10
    RATING_DOMINANCE_THRESHOLD = (
        0.8  # Threshold for high or low rating dominance in decimal
    )

    def load_data(self) -> None:
        pass

    def verify(self) -> bool:
        return self._is_dataframe_valid()

    def run(self) -> DataFrame:
        tqdm.pandas(desc="Running reviews insights enhancement")

        # Apply the enhancement function
        enhancements = self.df[self.REQUIRED_FIELDS["reviews_path"]].progress_apply(
            self._enhance_review_insights
        )
        log.debug(f"EXTRACTED DATA FRAME {enhancements}")

        # Convert the enhancements into a DataFrame and join it with self.df
        enhancements_df = pd.DataFrame(enhancements.tolist(), index=self.df.index)
        self.df = self.df.join(enhancements_df)

        return self.df

    def finish(self) -> None:
        pass

    def _check_api_key(self, api_key, api_name):
        if api_key is None:
            raise StepError(f"An API key for {api_name} is needed to run this step!")

    def _enhance_review_insights(self, reviews_path):
        if not self._is_valid_place_id(reviews_path):
            return pd.Series({f"{col}": None for col in self.added_cols})
        reviews = self._fetch_reviews(reviews_path)
        if not reviews:
            return pd.Series({f"{col}": None for col in self.added_cols})
        log.debug(f"FETCHED REVIEWS : {reviews}")
        reviews_langs = [
            {
                "text": review.get("text", ""),
                "lang": review.get("original_language", "en-US"),
            }
            for review in reviews
        ]
        log.debug(f"EXTRACTED REVIEW AND LANG : {reviews_langs}")

        avg_gram_sco = self._calculate_average_grammatical_score(reviews_langs)
        log.debug(f"AVG GRAM SCORE : {avg_gram_sco}")

        ratings = [
            review["rating"]
            for review in reviews
            if "rating" in review and review["rating"] is not None
        ]
        log.debug(f"EXTRACTED RATINGS : {ratings}")

        (
            polarization_type,
            polarization_score,
            highest_rating_ratio,
            lowest_rating_ratio,
        ) = self._quantify_polarization(ratings)
        log.debug(
            f"POLARIZATION VALUES : type: {polarization_type}, score: {polarization_score}, high_ratio: {highest_rating_ratio}, low_ratio:{lowest_rating_ratio}"
        )
        rating_time = [
            {
                "time": review.get("time"),
                "rating": review.get("rating"),
            }
            for review in reviews
        ]
        log.debug(f"EXTRACTED RATINGS AND TIMES: {rating_time}")

        rating_trend = self._analyze_rating_trend(rating_time)

        log.debug(f"ANALYZED RATINGS AND TIMES: {rating_trend}")

        extracted_features = {
            "review_avg_grammatical_score": avg_gram_sco,
            "review_polarization_type": polarization_type,
            "review_polarization_score": polarization_score,
            "review_highest_rating_ratio": highest_rating_ratio,
            "review_lowest_rating_ratio": lowest_rating_ratio,
            "review_rating_trend": rating_trend,
        }
        log.debug(f"Extracted feats : {extracted_features}")
        return pd.Series({f"{col}": extracted_features[col] for col in self.added_cols})

    def _analyze_rating_trend(self, rating_time):
        """
        Analyzes the general trend of ratings over time.

        :param reviews: List of review data, each a dict with 'time' (Unix timestamp) and 'rating'.
        :return: A value between -1 and 1 indicating the trend of ratings.
            - A value close to 1 indicates a strong increasing trend.
            - A value close to -1 indicates a strong decreasing trend.
            - A value around 0 indicates no significant trend (stable ratings).
        """
        # Convert to DataFrame
        df = pd.DataFrame(rating_time)

        # Convert Unix timestamp to numerical value (e.g., days since the first review)
        df["date"] = pd.to_datetime(df["time"], unit="s")
        df["days_since_start"] = (df["date"] - df["date"].min()).dt.days

        # Linear regression
        model = LinearRegression()
        model.fit(df[["days_since_start"]], df["rating"])

        # Slope of the regression line
        slope = model.coef_[0]

        # Normalize the slope to be within the range [-1, 1]
        slope_normalized = np.clip(slope, -1, 1)

        return slope_normalized

    def _quantify_polarization(self, ratings: list):
        """
        Analyzes and quantifies the polarization in a list of ratings.

        Returns:
            Tuple: A tuple containing the polarization type, polarization score,
                highest rating ratio, lowest rating ratio, rating counts,
                and total number of ratings.
        """

        total_ratings = len(ratings)
        if total_ratings <= self.MIN_RATINGS_COUNT:
            log.info(f"There is no sufficient data to identify polarization")
            return "Insufficient data", None, None, None

        rating_counts = Counter(ratings)
        high_low_count = rating_counts.get(5, 0) + rating_counts.get(1, 0)
        high_low_ratio = high_low_count / total_ratings
        middle_ratio = (total_ratings - high_low_count) / total_ratings
        highest_rating_ratio = rating_counts.get(5, 0) / total_ratings
        lowest_rating_ratio = rating_counts.get(1, 0) / total_ratings
        polarization_score = high_low_ratio - middle_ratio

        polarization_type = self._determine_polarization_type(
            polarization_score,
            highest_rating_ratio,
            lowest_rating_ratio,
            self.RATING_DOMINANCE_THRESHOLD,
        )

        return (
            polarization_type,
            polarization_score,
            highest_rating_ratio,
            lowest_rating_ratio,
        )

    def _determine_polarization_type(
        self, polarization_score, highest_rating_ratio, lowest_rating_ratio, threshold
    ):
        """
        Determines the type of polarization based on rating ratios and a threshold.
        """
        if polarization_score > 0:
            if highest_rating_ratio > threshold:
                return "High Rating Dominance"
            elif lowest_rating_ratio > threshold:
                return "Low Rating Dominance"
            return "High-Low Polarization"
        return "Balanced"

    def _calculate_average_grammatical_score(self, reviews):
        if not reviews:
            return 0
        scores = [
            self._calculate_score(review)
            for review in reviews
            if self._is_review_valid(review)
        ]
        return sum(scores) / len(scores) if scores else 0

    def _calculate_score(self, review):
        num_errors = self._grammatical_errors(review["text"], review["lang"])
        num_words = len(review["text"].split())
        if num_words == 0:
            return 1
        return max(1 - (num_errors / num_words), 0)

    def _grammatical_errors(self, text, lang="en-US"):
        try:
            tool = ltp.LanguageTool(lang)
            errors = tool.check(text)
            return len(errors)
        except Exception as e:
            log.error(f"An error occurred in grammatical_errors: {e}")
            return 0

    def _fetch_reviews(self, reviews_path):
        try:
            # reviews_path always starts with "./data/.."
            full_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../../" + reviews_path)
            )
            with open(full_path, "r", encoding="utf-8") as reviews_json:
                reviews = json.load(reviews_json)
                return reviews
        except:
            log.warning(f"Error loading reviews from path {full_path}.")
            # Return empty list if any exception occurred or status is not OK
            return []

    def _is_valid_place_id(self, place_id):
        """
        Checks if the place_id is valid (not None and not NaN).
        """
        return place_id is not None and not pd.isna(place_id)

    def _is_review_valid(self, review):
        """
        Checks if the review is valid (has text and original language).
        """
        return not (review["text"] is None or review["lang"] is None)

    def _is_dataframe_valid(self):
        """
        Validates if the DataFrame has the required fields.
        """
        return self.df is not None and all(
            column in self.df for column in self.REQUIRED_FIELDS.values()
        )
