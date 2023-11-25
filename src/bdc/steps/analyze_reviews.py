# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Berkay Bozkurt <resitberkaybozkurt@gmail.com>
# SPDX-FileCopyrightText: 2023 Sophie Heasman <sophieheasmann@gmail.com>


from http import HTTPStatus

import openai
import pandas as pd
import requests
from bs4 import BeautifulSoup
from pandas import DataFrame
from requests import RequestException
from tqdm import tqdm

from bdc.steps.step import Step, StepError
from config import OPEN_AI_API_KEY


class GPTReviewSentimentAnalyzer(Step):
    name = "GPT-ReviewSentimentAnalyzer"
    model = "gpt-4"
    no_answer = "None"
    gpt_required_fields = {"places_id": "google_places_place_id"}
    # system and user messages to be used for creating company summary for lead using website.
    system_message_for_sentiment_analysis = f"You are review sentiment analyzer, you being provided reviews of the companies. You analyze the review and come up with the score between range [-1, 1], if no reviews then just answer with '{no_answer}'"
    user_message_for_sentiment_analysis = "Sentiment analyze the reviews  and provide me a score between range [-1, 1]  : {}"

    extracted_col_name = "reviews_sentiment_score"
    client = None

    def load_data(self) -> None:
        self.client = openai.OpenAI(api_key=OPEN_AI_API_KEY)

    def verify(self) -> bool:
        if OPEN_AI_API_KEY is None:
            raise StepError("An API key for openAI is need to run this step!")
        return self.df is not None and all(
            column in self.df for column in self.gpt_required_fields
        )

    def run(self) -> DataFrame:
        tqdm.pandas(desc="Summarizing the website of leads")
        self.df[self.extracted_col_name] = self.df[
            self.gpt_required_fields["places_id"]
        ].progress_apply(lambda place_id: self.run_sentiment_analysis(place_id))
        return self.df

    def finish(self) -> None:
        pass

    def run_sentiment_analysis(self, place_id):
        """
        Runs sentiment analysis on reviews of lead extracted from company's website

        """

        # if there is no place_id, then return without API call.
        if place_id is None or pd.isna(place_id):
            return None

    def summarize_the_company_website(self, website):
        """
        Summarise client website using GPT. Handles exceptions that mightarise from the API call.
        """

        if website is None or pd.isna(website):
            return None

        html = self.extract_the_raw_html_and_parse(website)

        if html is None:
            return None

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.system_message_for_website_summary,
                    },
                    {
                        "role": "user",
                        "content": self.user_message_for_website_summary.format(html),
                    },
                ],
                temperature=0,
            )

            # Check if the response contains the expected data
            if response.choices[0].message.content:
                company_summary = response.choices[0].message.content

                if company_summary == self.no_answer:
                    return None

                return company_summary
            else:
                self.log("No summary data found in the response.")
                return None
        except (
            openai.APITimeoutError,
            openai.APIConnectionError,
            openai.BadRequestErroras,
            openai.AuthenticationError,
            openai.PermissionDeniedError,
            Exception,
        ) as e:
            # Handle possible errors
            self.log(f"An error occurred during summarizing the lead with GPT: {e}")
            pass

    def extract_the_raw_html_and_parse(self, url):
        try:
            # Send a request to the URL
            response = requests.get(url)
        except RequestException as e:
            self.log(f"An error occured during getting repsonse from url: {e}")
            return None

        # If the request was not successful
        if not response.status_code == HTTPStatus.OK:
            self.log(f"Failed to fetch data. Status code: {response.status_code}")
            return None
        try:
            # Use the detected encoding to decode the response content
            soup = BeautifulSoup(response.content, "html.parser")

            texts = []
            for element in soup.find_all(["h1", "h2", "h3", "p", "li"]):
                texts.append(element.get_text(strip=True))
            return " ".join(texts)
        except UnicodeDecodeError as e:
            return None
