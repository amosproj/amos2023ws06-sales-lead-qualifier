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
from logger import get_logger

log = get_logger()


class GPTSummarizer(Step):
    name = "GPT-Summarizer"
    model = "gpt-4"
    no_answer = "None"

    # system and user messages to be used for creating company summary for lead using website.
    system_message_for_website_summary = f"You are html summarizer, you being provided the companies' htmls and you answer with the summary of three to five sentences including all the necessary information which might be useful for salesperson. If no html then just answer with '{no_answer}'"
    user_message_for_website_summary = (
        "Give salesperson a summary using following html: {}"
    )

    extracted_col_name_website_summary = "sales_person_summary"

    added_cols = [extracted_col_name_website_summary]

    client = None

    def load_data(self) -> None:
        self.client = openai.OpenAI(api_key=OPEN_AI_API_KEY)

    def verify(self) -> bool:
        if OPEN_AI_API_KEY is None:
            raise StepError("An API key for openAI is need to run this step!")
        return self.df is not None and "google_places_website" in self.df

    def run(self) -> DataFrame:
        tqdm.pandas(desc="Summarizing the website of leads")
        self.df[self.extracted_col_name_website_summary] = self.df.progress_apply(
            lambda lead: self.summarize_the_company_website(
                lead["google_places_website"]
            ),
            axis=1,
        )
        return self.df

    def finish(self) -> None:
        pass

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
                log.info("No summary data found in the response.")
                return None
        except (
            openai.APITimeoutError,
            openai.APIConnectionError,
            openai.BadRequestError,
            openai.AuthenticationError,
            openai.PermissionDeniedError,
            Exception,
        ) as e:
            # Handle possible errors
            log.error(f"An error occurred during summarizing the lead with GPT: {e}")
            pass

    def extract_the_raw_html_and_parse(self, url):
        try:
            # Send a request to the URL
            response = requests.get(url)
        except RequestException as e:
            log.error(f"An error occured during getting repsonse from url: {e}")
            return None

        # If the request was successful
        if not response.status_code == HTTPStatus.OK:
            log.error(f"Failed to fetch data. Status code: {response.status_code}")
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
