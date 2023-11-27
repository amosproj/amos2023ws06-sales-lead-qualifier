# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Berkay Bozkurt <resitberkaybozkurt@gmail.com>
# SPDX-FileCopyrightText: 2023 Sophie Heasman <sophieheasmann@gmail.com>

from collections import Counter
from http import HTTPStatus

import googlemaps
import language_tool_python as ltp
import openai
import pandas as pd
from googlemaps.exceptions import ApiError, HTTPError, Timeout, TransportError
from pandas import DataFrame
from requests import RequestException
from tqdm import tqdm

from bdc.steps.step import Step, StepError
from config import GOOGLE_PLACES_API_KEY, OPEN_AI_API_KEY
from logger import get_logger

log = get_logger()


class SmartReviewInsightsEnhancer(Step):
    NAME = "Smart-Review-Insights-Enhancer"
    MODEL = "gpt-4"
    MODEL_ENCODING_NAME = "cl100k_base"
    MAX_PROMPT_TOKENS = 4096
    NO_ANSWER = "None"
    REQUIRED_FIELDS = {"places_id": "google_places_place_id"}
    SYSTEM_MESSAGE_FOR_SENTIMENT_ANALYSIS = (
        "You are a review sentiment analyzer. You are being provided reviews of companies. "
        "Analyze the reviews and come up with a score between the range [-1, 1]. If there are no reviews, answer with '{}'."
    ).format(NO_ANSWER)
    USER_MESSAGE_FOR_SENTIMENT_ANALYSIS = (
        "Sentiment analyze the reviews and provide me a score between range [-1, 1]: {}"
    )
    EXTRACTED_COL_NAMES = {"g_sco": "reviews_grammatical_score"}
    ADDED_COLS = list(EXTRACTED_COL_NAMES.values())
    MIN_RATINGS_COUNT = 10
    RATING_DOMINANCE_THRESHOLD = (
        0.8  # Threshold for high or low rating dominance in decimal
    )

    gpt = None
    gmaps = None

    def load_data(self) -> None:
        self.gpt = openai.OpenAI(api_key=OPEN_AI_API_KEY)
        self.gmaps = googlemaps.Client(key=GOOGLE_PLACES_API_KEY)

    def verify(self) -> bool:
        self._check_api_key(OPEN_AI_API_KEY, "OpenAI")
        self._check_api_key(GOOGLE_PLACES_API_KEY, "Google Places")
        return self._is_dataframe_valid()

    def run(self) -> DataFrame:
        tqdm.pandas(desc="Running reviews insights enhancement")
        self.df[self.EXTRACTED_COL_NAMES["g_sco"]] = self.df[
            self.REQUIRED_FIELDS["places_id"]
        ].progress_apply(self._enhance_review_insights)
        return self.df

    def finish(self) -> None:
        pass

    def _check_api_key(self, api_key, api_name):
        if api_key is None:
            raise StepError(f"An API key for {api_name} is needed to run this step!")

    def _enhance_review_insights(self, place_id):
        if not self._is_valid_place_id(place_id):
            return None
        reviews = self._fetch_reviews(place_id)

        reviews_langs = [
            {
                "text": review.get("text", ""),
                "lang": review.get("original_language", "en-US"),
            }
            for review in reviews
        ]
        avg_gram_sco = self._calculate_average_grammatical_score(reviews_langs)

        ratings = [
            review["rating"]
            for review in reviews
            if "rating" in review and review["rating"] is not None
        ]
        (
            polarization_type,
            polarization_score,
            highest_rating_ratio,
            lowest_rating_ratio,
        ) = self._quantify_polarization(ratings)

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
            return "Insufficient data", None, None, None, {}, total_ratings

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
            return "High-Low Polarization"
        if highest_rating_ratio > threshold:
            return "High Rating Dominance"
        if lowest_rating_ratio > threshold:
            return "Low Rating Dominance"
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

    def _fetch_reviews(self, place_id):
        try:
            response = self.gmaps.place(place_id, fields=["name", "reviews"])
            if response.get("status") != HTTPStatus.OK.name:
                log.warning(
                    f"Failed to fetch data. Status code: {response.get('status')}"
                )
                return []
            return response.get("result", {}).get("reviews", [])
        except (ApiError, HTTPError, Timeout, TransportError, RequestException) as e:
            log.error(f"Error occurred while fetching reviews: {e}")
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
