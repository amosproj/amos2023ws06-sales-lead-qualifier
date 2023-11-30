# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Berkay Bozkurt <resitberkaybozkurt@gmail.com>
# SPDX-FileCopyrightText: 2023 Sophie Heasman <sophieheasmann@gmail.com>

import json
import os.path
import time
from collections import Counter

import language_tool_python as ltp
import numpy as np
import openai
import pandas as pd
import tiktoken
from pandas import DataFrame
from sklearn.linear_model import LinearRegression
from tqdm import tqdm

from bdc.steps.step import Step, StepError
from config import OPEN_AI_API_KEY
from logger import get_logger

log = get_logger()


"""
HELPER FUNCTIONS
"""


def is_review_valid(review):
    """
    Checks if the review is valid (has text and original language).
    """
    return not (review["text"] is None or review["lang"] is None)


def is_dataframe_valid(df):
    """
    Validates if the DataFrame has the required fields.
    """
    return df is not None and "google_places_detailed_reviews_path" in df


def is_valid_reviews_path(review_path):
    """
    Checks if the review_path is valid (not None and not NaN).
    """
    return review_path is not None and not pd.isna(review_path)


def check_api_key(api_key, api_name):
    if api_key is None:
        raise StepError(f"An API key for {api_name} is needed to run this step!")


def fetch_reviews(reviews_path):
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


"""
CLASSES
"""


class GPTReviewSentimentAnalyzer(Step):
    name = "GPT-Review-Sentiment-Analyzer"
    model = "gpt-4"
    model_encoding_name = "cl100k_base"
    MAX_PROMPT_TOKENS = 4096
    no_answer = "None"
    gpt_required_fields = {"reviews_path": "google_places_detailed_reviews_path"}
    # system and user messages to be used for creating company summary for lead using website.
    system_message_for_sentiment_analysis = f"You are review sentiment analyzer, you being provided reviews of the companies. You analyze the review and come up with the score between range [-1, 1], if no reviews then just answer with '{no_answer}'"
    user_message_for_sentiment_analysis = "Sentiment analyze the reviews  and provide me a score between range [-1, 1]  : {}"

    extracted_col_name = "reviews_sentiment_score"
    added_cols = [extracted_col_name]
    gpt = None

    def load_data(self) -> None:
        self.gpt = openai.OpenAI(api_key=OPEN_AI_API_KEY)

    def verify(self) -> bool:
        check_api_key(OPEN_AI_API_KEY, "OpenAI")

        return self.df is not None and all(
            column in self.df for column in self.gpt_required_fields.values()
        )

    def run(self) -> DataFrame:
        tqdm.pandas(desc="Running sentiment analysis on reviews")
        self.df[self.extracted_col_name] = self.df[
            self.gpt_required_fields["reviews_path"]
        ].progress_apply(lambda reviews_path: self.run_sentiment_analysis(reviews_path))
        return self.df

    def finish(self) -> None:
        pass

    def run_sentiment_analysis(self, reviews_path):
        """
        Runs sentiment analysis on reviews of lead extracted from company's website

        """

        # if there is no reviews_path, then return without API call.
        if not is_valid_reviews_path(reviews_path):
            return None
        reviews = fetch_reviews(reviews_path)
        review_texts = self.extract_text_from_reviews(reviews)
        if len(review_texts) == 0:
            return None
        review_ratings = [review.get("rating", None) for review in reviews]
        # batch reviews so that we do not exceed the token limit of gpt4
        review_batches = self.batch_reviews(review_texts, self.MAX_PROMPT_TOKENS)
        scores = 0
        # iterate over each batch and calculate average sentiment score
        for review_batch in review_batches:
            sentiment_score = self.gpt_sentiment_analyze_review(review_batch)
            scores += sentiment_score or 0
        scores
        return scores / len(review_batches)

    def gpt_sentiment_analyze_review(self, review_list):
        """
        GPT calculates the sentiment score considering the reviews
        """
        max_retries = 5  # Maximum number of retries
        retry_delay = 5  # Initial delay in seconds (5 seconds)

        for attempt in range(max_retries):
            try:
                response = self.gpt.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": self.system_message_for_sentiment_analysis,
                        },
                        {
                            "role": "user",
                            "content": self.user_message_for_sentiment_analysis.format(
                                review_list
                            ),
                        },
                    ],
                    temperature=0,
                )
                # Extract and return the sentiment score
                sentiment_score = response.choices[0].message.content
                if sentiment_score and sentiment_score != self.no_answer:
                    return float(sentiment_score)
                else:
                    log.info("No valid sentiment score found in the response.")
                    return None
            except openai.RateLimitError as e:
                if attempt < max_retries - 1:
                    log.warning(
                        f"Rate limit exceeded, retrying in {retry_delay} seconds..."
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    log.error("Max retries reached. Unable to complete the request.")
                    break
            except (
                openai.APITimeoutError,
                openai.APIConnectionError,
                openai.BadRequestError,
                openai.AuthenticationError,
                openai.PermissionDeniedError,
            ) as e:
                log.error(f"An error occurred with GPT API: {e}")
                break
            except Exception as e:
                log.error(f"An unexpected error occurred: {e}")
                break

        # Return None if the request could not be completed successfully
        return None

    def extract_text_from_reviews(self, reviews_list):
        """
        extracts text from reviews and removes line characters.
        """
        reviews_texts = [review.get("text", None) for review in reviews_list]
        review_texts_formatted = [
            review.strip().replace("\n", " ") for review in reviews_texts if review
        ]
        return review_texts_formatted

    def num_tokens_from_string(self, text: str):
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.get_encoding(self.model_encoding_name)
        num_tokens = len(encoding.encode(text))
        return num_tokens

    def batch_reviews(self, reviews, max_tokens=4096):
        """
        Batchs reviews into batches so that every batch has the size less than max_tokens
        """
        batches = []
        current_batch = []
        current_count = self.num_tokens_from_string(
            self.user_message_for_sentiment_analysis
        )

        for review in reviews:
            token_count = self.num_tokens_from_string(review)
            if current_count + token_count > max_tokens:
                batches.append(current_batch)
                current_batch = [review]
                current_count = token_count
            else:
                current_batch.append(review)
                current_count += token_count

        if current_batch:
            batches.append(current_batch)

        return batches


class SmartReviewInsightsEnhancer(Step):
    name = "Smart-Review-Insights-Enhancer"
    MIN_RATINGS_COUNT = 1
    RATING_DOMINANCE_THRESHOLD = (
        0.4  # Threshold for high or low rating dominance in decimal
    )

    added_cols = [
        "review_avg_grammatical_score",
        "review_polarization_type",
        "review_polarization_score",
        "review_highest_rating_ratio",
        "review_lowest_rating_ratio",
        "review_rating_trend",
    ]

    def load_data(self) -> None:
        pass

    def verify(self) -> bool:
        return is_dataframe_valid(self.df)

    def run(self) -> DataFrame:
        tqdm.pandas(desc="Running reviews insights enhancement")

        # Apply the enhancement function
        self.df[self.added_cols] = self.df.progress_apply(
            lambda lead: pd.Series(self._enhance_review_insights(lead)), axis=1
        )
        return self.df

    def finish(self) -> None:
        pass

    def _enhance_review_insights(self, lead):
        reviews_path = lead["google_places_detailed_reviews_path"]
        if not is_valid_reviews_path(reviews_path):
            return pd.Series({f"{col}": None for col in self.added_cols})
        reviews = fetch_reviews(reviews_path)
        if not reviews:
            return pd.Series({f"{col}": None for col in self.added_cols})
        results = []
        reviews_langs = [
            {
                "text": review.get("text", ""),
                "lang": review.get("original_language", "en-US"),
            }
            for review in reviews
        ]
        avg_gram_sco = self._calculate_average_grammatical_score(reviews_langs)
        results.append(avg_gram_sco)

        ratings = [
            review["rating"]
            for review in reviews
            if "rating" in review and review["rating"] is not None
        ]

        polarization_results = list(self._quantify_polarization(ratings))
        results += polarization_results

        rating_time = [
            {
                "time": review.get("time"),
                "rating": review.get("rating"),
            }
            for review in reviews
        ]

        rating_trend = self._analyze_rating_trend(rating_time)
        results.append(rating_trend)

        extracted_features = dict(zip(self.added_cols, results))

        return pd.Series(extracted_features)

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

        # Replace -0 with 0
        return 0 if slope_normalized == 0 else slope_normalized

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
                return "High-Rating Dominance"
            elif lowest_rating_ratio > threshold:
                return "Low-Rating Dominance"
            return "High-Low Polarization"
        return "Balanced"

    def _calculate_average_grammatical_score(self, reviews):
        if not reviews:
            return 0
        scores = [
            self._calculate_score(review)
            for review in reviews
            if is_review_valid(review)
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
