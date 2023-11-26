# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Berkay Bozkurt <resitberkaybozkurt@gmail.com>
# SPDX-FileCopyrightText: 2023 Sophie Heasman <sophieheasmann@gmail.com>


from http import HTTPStatus

import googlemaps
import openai
import pandas as pd
from googlemaps.exceptions import ApiError, HTTPError, Timeout, TransportError
from pandas import DataFrame
from requests import RequestException
from tqdm import tqdm

from bdc.steps.step import Step, StepError
from config import GOOGLE_PLACES_API_KEY, OPEN_AI_API_KEY


class GPTReviewSentimentAnalyzer(Step):
    name = "GPT-Review-Sentiment-Analyzer"
    model = "gpt-4"
    MAX_PROMPT_TOKENS = 4096
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

        return scores / len(review_batches)

    def gpt_sentiment_analyze_review(self, review_list):
        """
        GPT calculates the sentiment score considering the reviews
        """
        try:
            response = self.client.chat.completions.create(
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
            self.log(f"GPT response {sentiment_score}")
            if sentiment_score and sentiment_score != self.no_answer:
                return float(sentiment_score)
            else:
                self.log("No valid sentiment score found in the response.")
                return None

        except (
            openai.APITimeoutError,
            openai.APIConnectionError,
            openai.BadRequestError,
            openai.AuthenticationError,
            openai.PermissionDeniedError,
        ) as e:
            self.log(f"An error occurred with GPT API: {e}")
        except Exception as e:
            self.log(f"An unexpected error occurred: {e}")

        # Return None if any exception occurred
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

    def tokenize(self, text):
        # Rough estimation of token count
        return len(text) // 4

    def batch_reviews(self, reviews, max_tokens=4096):
        """
        Batchs reviews into batches so that every batch has the size less than max_tokens
        """
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
