# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Berkay Bozkurt <resitberkaybozkurt@gmail.com>
# SPDX-FileCopyrightText: 2023 Sophie Heasman <sophieheasmann@gmail.com>
import json
import os.path
import time

import openai
import pandas as pd
import tiktoken
from pandas import DataFrame
from tqdm import tqdm

from bdc.steps.step import Step, StepError
from config import OPEN_AI_API_KEY
from database import get_database
from logger import get_logger

log = get_logger()


class GPTReviewSentimentAnalyzer(Step):
    """
    The GPTReviewSentiment Analyzer step will read reviews obtained for a business (e.g. from Google Maps) and perform
    sentiment analysis using OpenAI GPT3/4.

    Attributes:
        name: Name of this step, used for logging
        added_cols: List of fields that will be added to the main dataframe by executing this step
        required_cols: List of fields that are required to be existent in the input dataframe before performing this step
    """

    name = "GPT-Review-Sentiment-Analyzer"
    model = "gpt-4"
    model_encoding_name = "cl100k_base"
    MAX_PROMPT_TOKENS = 4096
    no_answer = "None"
    gpt_required_fields = {"place_id": "google_places_place_id"}
    # system and user messages to be used for creating company summary for lead using website.
    system_message_for_sentiment_analysis = f"You are review sentiment analyzer, you being provided reviews of the companies. You analyze the review and come up with the score between range [-1, 1], if no reviews then just answer with '{no_answer}'"
    user_message_for_sentiment_analysis = "Sentiment analyze the reviews  and provide me a score between range [-1, 1]  : {}"

    extracted_col_name = "reviews_sentiment_score"
    added_cols = [extracted_col_name]
    required_cols = gpt_required_fields.values()
    gpt = None

    def load_data(self) -> None:
        self.gpt = openai.OpenAI(api_key=OPEN_AI_API_KEY)

    def verify(self) -> bool:
        self.check_api_key(OPEN_AI_API_KEY, "OpenAI")

        return self.df is not None and all(
            column in self.df for column in self.required_cols
        )

    def run(self) -> DataFrame:
        tqdm.pandas(desc="Running sentiment analysis on reviews")
        self.df[self.extracted_col_name] = self.df[
            self.gpt_required_fields["place_id"]
        ].progress_apply(lambda place_id: self.run_sentiment_analysis(place_id))
        return self.df

    def finish(self) -> None:
        pass

    def check_api_key(self, api_key, api_name):
        if api_key is None:
            raise StepError(f"An API key for {api_name} is needed to run this step!")

    def run_sentiment_analysis(self, place_id):
        """
        Runs sentiment analysis on reviews of lead extracted from company's website

        """

        # if there is no reviews_path, then return without API call.
        if place_id is None or pd.isna(place_id):
            return None
        reviews = get_database().fetch_review(place_id)
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
                log.debug(f"GPT response {sentiment_score}")
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
