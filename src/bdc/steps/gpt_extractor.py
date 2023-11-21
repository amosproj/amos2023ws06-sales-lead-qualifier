# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Berkay Bozkurt <resitberkaybozkurt@gmail.com>

from http import HTTPStatus

import openai
import requests
from bs4 import BeautifulSoup
from pandas import DataFrame
from requests import RequestException
from tqdm import tqdm

from bdc.steps.step import Step, StepError
from config import OPEN_AI_API_KEY


class GPTExtractor(Step):
    name = "GPT-Extractor"
    model = "gpt-4"
    no_answer = "None"
    # system and user messages to be used for extracting domains from by lead provided email address.
    system_message_for_website_summary = f"You are html summarizer, you being provided the companies' htmls and you answer with the summary of three to five sentences including all the necessary information which might be useful for salesperson. If no html then just answer with '{no_answer}'"
    user_message_for_website_summary = (
        "Give salesperson a summary using following html: {}"
    )

    extracted_col_name_website_summary = "sales_person_summary"

    client = None

    def load_data(self) -> None:
        self.client = openai.OpenAI(api_key=OPEN_AI_API_KEY)

    def verify(self) -> bool:
        if OPEN_AI_API_KEY is None:
            raise StepError("An API key for openAI is need to run this step!")
        return self.df is not None and "google_places_website" in self.df

    def run(self) -> DataFrame:
        tqdm.pandas(desc="Summarizing the website of leads")
        self.df[self.extracted_col_name_website_summary] = self.df[
            "google_places_website"
        ].progress_apply(lambda lead: self.summarize_the_company_website(lead))
        return self.df

    def finish(self) -> None:
        pass

    def summarize_the_company_website(self, website):
        """
        Extract address using GPT for a given lead. Handles exceptions that mightarise from the API call.
        """
        if website is None:
            return None
        html_raw = self.extract_the_raw_html_from_url(website)
        if html_raw is None:
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
                        "content": self.user_message_for_website_summary.format(
                            html_raw
                        ),
                    },
                ],
                temperature=0,
            )
            # Check if the response contains the expected data
            if response.choices[0].message.content:
                company_address = response.choices[0].message.content
                # self.log(f"Extracted company address: {company_address}")
                if company_address == self.no_answer:
                    return None
                return company_address
            else:
                self.log("No company address data found in the response.")
                return None
        except openai.APITimeoutError as e:
            # Handle timeout error, e.g. retry or log
            self.log(f"OpenAI API request timed out: {e}")
            pass
        except openai.APIConnectionError as e:
            # Handle connection error, e.g. check network or log
            self.log(f"OpenAI API request failed to connect: {e}")
            pass
        except openai.BadRequestError as e:
            # Handle invalid request error, e.g. validate parameters or log
            self.log(f"OpenAI API request was bad: {e}")
            pass
        except openai.AuthenticationError as e:
            # Handle authentication error, e.g. check credentials or log
            self.log(f"OpenAI API request was not authorized: {e}")
            pass
        except openai.PermissionDeniedError as e:
            # Handle permission error, e.g. check scope or log
            self.log(f"OpenAI API request was not permitted: {e}")
            pass
        except Exception as e:
            self.log(f"An error occurred during address extraction: {e}")
            # Optionally, you might want to re-raise the exception
            # or handle it differently depending on your use case.
            return None

    def extract_the_raw_html_from_url(self, url):
        try:
            # Send a request to the URL
            response = requests.get(url)
        except RequestException as e:
            return None

        # If the request was successful
        if response.status_code == HTTPStatus.OK:
            # Detect the correct encoding
            # if 'charset' in response.headers.get('content-type', '').lower():
            # encoding = response.apparent_encoding
            # else:
            #     encoding = response.encoding
            encoding = "utf-8"

            try:
                # Use the detected encoding to decode the response content
                soup = BeautifulSoup(response.content, "html.parser")

                texts = []
                for element in soup.find_all(["h1", "h2", "h3", "p", "li"]):
                    texts.append(element.get_text(strip=True))
                return " ".join(texts)
            except UnicodeDecodeError as e:
                return None

            # Store the decoded HTML
            return None
        return None
