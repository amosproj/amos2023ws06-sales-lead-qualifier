# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Berkay Bozkurt <resitberkaybozkurt@gmail.com>

import openai
from pandas import DataFrame
from tqdm import tqdm

from bdc.steps.step import Step, StepError
from config import OPEN_AI_API_KEY


class GPTExtractor(Step):
    name = "GPT-Extractor"
    model = "gpt-4"
    no_answer = "None"
    # system and user messages to be used for extracting domains from by lead provided email address.
    system_message_for_domain_extraction = f"You are a domain extractor, which extracts possible domains from given email addresses. You just provide domains in such a format <email-domain>, if no valid email address given then just povide {no_answer}"
    user_message_for_domain_extraction = (
        "Extract domain from following email address: {}"
    )

    system_message_for_company_name_extraction = f"You are a look up table, specialized in finding and validating companies from provided email addresses, company names and personal infos. You just provide company name in such a format <company-name>, if provided company name is the same with provided personal infos, then search for possible companies that person might own or might be working for and provide the most up-to date company name, if you can not find any info then provide {no_answer}"
    user_message_for_company_name_extraction = "Find the company name using following infos Last Name: {}, First Name: {}, Company name: {}, email-address: {}, domain: {}"

    # system and user messages to be used for extracting company addresses from extracted domain
    system_message_for_company_address_extraction = f"You are a look up table, specialized in finding the companies for given company names, phone numbers and emails addresses. You just provide answers in format '<company_address_street_name> <company_address_street_number>, <company_address_postal_code>, <company_address_city>, <company_address_country>'. If you can not find any info about companies address then just provide {no_answer}' "
    user_message_for_company_address_extraction = "Extract company address from following informations company name: {}, phone number: {}, email-address: {}"
    extracted_col_name_domain_prefix = "gpt_extracted_domain"

    client = None

    def load_data(self) -> None:
        self.client = openai.OpenAI(api_key=OPEN_AI_API_KEY)

    def verify(self) -> bool:
        if OPEN_AI_API_KEY is None:
            raise StepError("An API key for openAI is need to run this step!")
        return self.df is not None

    def run(self) -> DataFrame:
        tqdm.pandas(desc="Extracting domains with GPT")
        self.df["domain"] = self.df.progress_apply(
            lambda lead: self.extract_domain_with_gpt(lead), axis=1
        )

        tqdm.pandas(desc="Extracting company names with GPT")
        self.df["Company / Account"] = self.df.progress_apply(
            lambda lead: self.extract_company_names_with_gpt(lead), axis=1
        )

        tqdm.pandas(desc="Extracting company addresses with GPT")
        self.df["google_places_formatted_address"] = self.df.progress_apply(
            lambda lead: self.extract_company_addresses_with_gpt(lead), axis=1
        )

        return self.df

    def finish(self) -> None:
        pass

    def extract_company_addresses_with_gpt(self, lead):
        """
        Extract address using GPT for a given lead. Handles exceptions that mightarise from the API call.
        """
        try:
            company_name = (
                lead["Company / Account"] if lead["Company / Account"] else None
            )
            phone = lead["Phone"] if lead["Phone"] else None
            email_addresss = lead["Email"] if lead["Email"] else None
            self.log(f"Checking the company address for company {company_name}")
            # check first if the domain is None, yes -> then extract it
            if lead["google_places_formatted_address"] is not None:
                return lead["google_places_formatted_address"]
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.system_message_for_company_address_extraction,
                    },
                    {
                        "role": "user",
                        "content": self.user_message_for_company_address_extraction.format(
                            company_name, phone, email_addresss
                        ),
                    },
                ],
                temperature=0,
            )
            # Check if the response contains the expected data
            if response.choices[0].message.content:
                company_address = response.choices[0].message.content
                self.log(f"Extracted company address: {company_address}")
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

    def extract_company_names_with_gpt(self, lead):
        """
        Extract address using GPT for a given lead. Handles exceptions that mightarise from the API call.
        """
        try:
            self.log(f"Checking the company name for lead {lead}")
            # check first if the domain is None, yes -> then extract it
            last_name = lead["Last Name"] if lead["Last Name"] else None
            first_name = lead["First Name"] if lead["First Name"] else None
            company_name = (
                lead["Company / Account"] if lead["Company / Account"] else None
            )
            phone = lead["Phone"] if lead["Phone"] else None
            email_addresss = lead["Email"] if lead["Email"] else None
            domain = lead["domain"] if lead["domain"] else None
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.system_message_for_company_name_extraction,
                    },
                    {
                        "role": "user",
                        "content": self.user_message_for_company_name_extraction.format(
                            last_name,
                            first_name,
                            company_name,
                            phone,
                            email_addresss,
                            domain,
                        ),
                    },
                ],
                temperature=0,
            )
            # Check if the response contains the expected data
            if response.choices[0].message.content:
                company = response.choices[0].message.content
                self.log(f"Extracted company name: {company}")
                if company == self.no_answer:
                    return None
                return company
            else:
                self.log("No company name data found in the response.")
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

    def extract_domain_with_gpt(self, lead):
        """
        Extract address using GPT for a given lead. Handles exceptions that mightarise from the API call.
        """
        try:
            # check first if the domain is None, yes -> then extract it
            if lead["domain"] is not None:
                return lead["domain"]
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.system_message_for_domain_extraction,
                    },
                    {
                        "role": "user",
                        "content": self.user_message_for_domain_extraction.format(
                            lead["Email"]
                        ),
                    },
                ],
                temperature=0,
            )
            # Check if the response contains the expected data
            if response.choices[0].message.content:
                domain = response.choices[0].message.content
                self.log(f"Extracted domain: {domain}")
                if domain == self.no_answer:
                    return None
                return domain
            else:
                self.log("No domain data found in the response.")
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
