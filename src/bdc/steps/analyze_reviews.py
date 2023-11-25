# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Berkay Bozkurt <resitberkaybozkurt@gmail.com>
# SPDX-FileCopyrightText: 2023 Sophie Heasman <sophieheasmann@gmail.com>


from http import HTTPStatus

import googlemaps
import openai
import pandas as pd
import requests
from bs4 import BeautifulSoup
from googlemaps.exceptions import ApiError, HTTPError, Timeout, TransportError
from pandas import DataFrame
from requests import RequestException
from tqdm import tqdm

from bdc.steps.step import Step, StepError
from config import GOOGLE_PLACES_API_KEY, OPEN_AI_API_KEY


class GPTReviewSentimentAnalyzer(Step):
    name = "GPT-Review-Sentiment-Analyzer"
    model = "gpt-4"
    no_answer = "None"
    gpt_required_fields = {"places_id": "google_places_place_id"}
    # system and user messages to be used for creating company summary for lead using website.
    system_message_for_sentiment_analysis = f"You are review sentiment analyzer, you being provided reviews of the companies. You analyze the review and come up with the score between range [-1, 1], if no reviews then just answer with '{no_answer}'"
    user_message_for_sentiment_analysis = "Sentiment analyze the reviews  and provide me a score between range [-1, 1]  : {}"

    extracted_col_name = "reviews_sentiment_score"
    gpt = None
    gmaps = None

    def load_data(self) -> None:
        self.client = openai.OpenAI(api_key=OPEN_AI_API_KEY)
        self.gmaps = googlemaps.Client(key=GOOGLE_PLACES_API_KEY)

    def verify(self) -> bool:
        self.check_api_key(OPEN_AI_API_KEY, "OpenAI")
        self.check_api_key(GOOGLE_PLACES_API_KEY, "Google Places")

        return self.df is not None and all(
            column in self.df for column in self.gpt_required_fields.values()
        )

    def run(self) -> DataFrame:
        tqdm.pandas(desc="Running sentiment analysis on reviews")
        self.df[self.extracted_col_name] = self.df[
            self.gpt_required_fields["places_id"]
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

        # if there is no place_id, then return without API call.
        if place_id is None or pd.isna(place_id):
            return None
        reviews = self.fetch_reviews(place_id)
        review_texts = self.extract_text_from_reviews(reviews)
        review_ratings = [review.get("rating", None) for review in reviews]
        self.log(f"Formatted review texts {review_texts}")

        review_batches = self.batch_reviews(review_texts)

    def extract_text_from_reviews(self, reviews_list):
        reviews_texts = [review.get("text", None) for review in reviews_list]
        review_texts_formatted = [
            review.strip().replace("\n", " ") for review in reviews_texts if review
        ]
        return review_texts_formatted

    def tokenize(self, text):
        # Rough estimation of token count
        return len(text) // 4

    def batch_reviews(self, reviews, max_tokens=4096):
        batches = []
        current_batch = []
        current_count = self.tokenize(self.user_message_for_sentiment_analysis)

        for review in reviews:
            token_count = self.tokenize(review)
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

    def fetch_reviews(self, place_id):
        try:
            # Fetch place details including reviews
            response = self.gmaps.place(place_id, fields=["name", "reviews"])

            # Check response status
            if response.get("status") != HTTPStatus.OK.name:
                self.log(f"Failed to fetch data. Status code: {response.get('status')}")
                return None

            # Extract reviews
            return response.get("result", None).get("reviews", [])

        except RequestException as e:
            self.log(f"Error: {str(e)}")

        except (ApiError, HTTPError, Timeout, TransportError) as e:
            error_message = (
                str(e.message)
                if hasattr(e, "message") and e.message is not None
                else str(e)
            )
            self.log(f"Error: {error_message}")

        # Return empty list if any exception occurred or status is not OK
        return []

    def fetch_website(self, place_id):
        try:
            website_response = self.gmaps.place(place_id, fields=["website"])

            # Check response status
            if website_response.get("status") != HTTPStatus.OK.name:
                self.log(
                    f"Failed to fetch data. Status code: {website_response.get('status')}"
                )
                return None

            # Extract website URL
            return website_response.get("result", None).get("website")

        except RequestException as e:
            self.log(f"Error: {str(e)}")

        except (ApiError, HTTPError, Timeout, TransportError) as e:
            error_message = (
                str(e.message)
                if hasattr(e, "message") and e.message is not None
                else str(e)
            )
            self.log(f"Error: {error_message}")

        # Return None if any exception occurred or status is not OK
        return None
