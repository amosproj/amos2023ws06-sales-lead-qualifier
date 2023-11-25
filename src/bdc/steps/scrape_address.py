# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lucca Baumgärtner <lucca.baumgaertner@fau.de>
import json
import re
from json import JSONDecodeError

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests import RequestException
from tqdm import tqdm

from bdc.steps.step import Step


class ScrapeAddress(Step):
    """
    A data enrichment step, scraping the leads website for an address using regex.
    """

    name = "Scrape-Address"
    added_cols = ["address_ver_1"]

    def load_data(self):
        # nothing to be done, we expect self.df to be set
        pass

    def verify(self):
        return self.df is not None and "domain" in self.df and "Email" in self.df

    def run(self):
        tqdm.pandas(desc="Getting addresses from custom domains...")
        # Approach 1: use the custom domain and parse this website
        self.df["address_ver_1"] = self.df[self.df["domain"].notna()].progress_apply(
            lambda lead: scrape_for_address(lead["domain"]), axis=1
        )

        return self.df

    def finish(self):
        p_address = self._df["address_ver_1"].notna().sum() / len(self._df) * 100
        self.log(f"Percentage of addresses scraped: {p_address:.2f}%")


def scrape_for_address(domain):
    if domain is None or pd.isna(domain):
        return None

    try:
        # Send a request to the URL
        response = requests.get("https://" + domain)
    except RequestException as e:
        return None

    # If the request was successful
    if response.status_code == 200:
        # Detect the correct encoding
        # if 'charset' in response.headers.get('content-type', '').lower():
        # encoding = response.apparent_encoding
        # else:
        #     encoding = response.encoding
        encoding = "utf-8"

        try:
            # Use the detected encoding to decode the response content
            response_text = response.content.decode(encoding)
        except UnicodeDecodeError as e:
            return None

        # Store the decoded HTML
        website_html = response_text

        # Use regex to find a German address with optional letter after house number
        address_pattern = re.compile(
            r"\b[A-Za-zäöüßÄÖÜ]+\.?\s+\d+(\s*-\s*\d+)?\w?,\s+\d{5}\s+[A-Za-zäöüßÄÖÜ]+\b"
        )

        # Search the text for the pattern
        address = address_pattern.findall(website_html)

        if address:
            address = address[0]  # Store the first match
        else:
            address = alternative_scrape_for_address(website_html)

        return address  # Return the first match
    return None


def alternative_scrape_for_address(raw_html):
    """
    Alternative approach to scrape for an address.
    :return:
    """
    # ... within your function
    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(raw_html, "html.parser")

    # Find the application/ld+json script tag
    script = soup.find("script", {"type": "application/ld+json"})

    address = None

    if script:
        try:
            # Parse the JSON content
            json_data = json.loads(script.string)
        except JSONDecodeError as e:
            return None

        # Extract the address information
        try:
            address_info = json_data.get("address")
            if address_info:
                street_address = address_info.get("streetAddress")
                address_locality = address_info.get("addressLocality")
                address = f"{street_address}, {address_locality}"
        except AttributeError as e:
            pass

    return address
