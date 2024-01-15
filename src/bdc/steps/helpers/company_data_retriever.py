# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Berkay Bozkurt <resitberkaybozkurt@gmail.com>

import requests
from bs4 import BeautifulSoup
from deutschland.bundesanzeiger import Bundesanzeiger

from logger import get_logger

log = get_logger()

OFFENREGISTER_BASE_URL = "https://db.offeneregister.de/"
OFFENRENREGISTER_POSITIONS_URL = (
    OFFENREGISTER_BASE_URL
    + "openregister/Positions?firstName__contains={}&lastName__contains={}"
)

OFFENREGISTER_CAPITAL_URL = (
    OFFENREGISTER_BASE_URL + "openregister/Capital?companyId__contains={}"
)

OFFENREGISTER_ADDRESSES_URL = (
    OFFENREGISTER_BASE_URL + "openregister/Addresses?companyId__contains={}"
)

OFFENREGISTER_NAMES_URL = (
    OFFENREGISTER_BASE_URL + "openregister/Names?companyId__contains={}"
)

OFFENREGISTER_OBJECTIVES_URL = (
    OFFENREGISTER_BASE_URL + "openregister/Objectives?companyId__contains={}"
)


class CompanyDataRetriever:
    """
    A class that retrieves company data from various sources based on given parameters.

    Methods:
        _find_from_Positions_by_firstName_and_lastName(last_name: str, first_name: str) -> dict:
            Retrieves company data from Positions table based on the last name and first name of a person.

        _find_row_by_companyId(url: str, company_id: str) -> dict:
            Finds and retrieves the row data for a given company ID from a specified URL.

        _find_from_Capital_by_companyId(company_id: str) -> dict:
            Retrieves company data from the Capital database using the provided company ID.

        _find_from_Addresses_by_companyId(company_id: str) -> dict:
            Retrieves the row from the Addresses table based on the given company ID.

        _find_from_Objectives_by_companyId(company_id: str) -> dict:
            Retrieves the row from Objectives by the given company ID.

        _find_from_Names_by_companyId(company_id: str) -> dict:
            Retrieves company data by company ID from the offerenregister.de website.

        find_companyName_by_lastName_firstName(last_name: str, first_name: str) -> str:
            Finds the company name by the last name and first name of a person.

        find_companyCapitals_by_lastName_firstName(last_name: str, first_name: str) -> tuple:
            Retrieves the capital amount and currency of a company based on the last name and first name of a person.

        find_companyObjective_by_lastName_firstName(last_name: str, first_name: str) -> str or None:
            Finds the company objective based on the last name and first name of a person.
    """

    def __init__(self) -> None:
        pass

    def _find_from_Positions_by_firstName_and_lastName(
        self, last_name: str, first_name: str
    ) -> dict:
        """
        Retrieves company data from Positions by using the first name and last name of a person.

        Args:
            last_name (str): The last name of the person.
            first_name (str): The first name of the person.

        Returns:
            dict: A dictionary containing class name and value pairs of the retrieved data.
        """
        url = OFFENRENREGISTER_POSITIONS_URL.format(first_name, last_name)
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # get table with class name rows-and-columns
            soup = BeautifulSoup(response.text, "html.parser")

            # Find the div with the specified class name
            div = soup.find("div", {"class": "table-wrapper"})

            # Find the table within the div
            table = div.find("table", {"class": "rows-and-columns"})

            # Access the tbody element
            tbody = table.tbody

            # Find all tr elements within the tbody
            rows = tbody.find_all("tr")

            # Print the number of tr elements
            # Get the first row
            first_row = rows[0]

            # Find all td elements within the first row
            columns = first_row.find_all("td")

            # Create a dictionary to store class name and value pairs
            col_dict = {}

            # Iterate over each column
            for column in columns:
                # Get the class name of the column
                class_name = column.get("class")[0] if column.get("class") else None

                # Get the text within the column
                value = column.text

                # Add the class name and value pair to the dictionary
                if class_name:
                    col_dict[class_name] = value

            # Print the dictionary
            return col_dict
        else:
            log.warn(f"Request failed with status code {response.status_code}")
            return None

    def _find_row_by_companyId(self, url, company_id) -> dict:
        """
        Finds and retrieves the row data for a given company ID from a specified URL.

        Args:
            url (str): The URL to retrieve the data from.
            company_id (str): The ID of the company to search for.

        Returns:
            dict: A dictionary containing the class name and value pairs for the first row of the table,
                  or None if the request fails or the company ID is not valid.
        """
        if company_id:
            url = url.format(company_id)
            response = requests.get(url)

            # Check if the request was successful
            if response.status_code == 200:
                # get table with class name rows-and-columns
                soup = BeautifulSoup(response.text, "html.parser")

                # Find the div with the specified class name
                div = soup.find("div", {"class": "table-wrapper"})

                # Find the table within the div
                table = div.find("table", {"class": "rows-and-columns"})

                # Access the tbody element
                tbody = table.tbody
                # Find all tr elements within the tbody
                rows = tbody.find_all("tr")

                # Print the number of tr elements
                # Get the first row
                first_row = rows[0]

                # Find all td elements within the first row
                columns = first_row.find_all("td")

                # Create a dictionary to store class name and value pairs
                col_dict = {}

                # Iterate over each column
                for column in columns:
                    # Get the class name of the column
                    class_name = column.get("class")[0] if column.get("class") else None

                    # Get the text within the column
                    value = column.text

                    # Add the class name and value pair to the dictionary
                    if class_name:
                        col_dict[class_name] = value

                # Print the dictionary
                log.info(col_dict)
                return col_dict
            else:
                log.warn(f"Request failed with status code {response.status_code}")
                return None
        else:
            log.info("Company id is not valid")
            return None

    def _find_from_Capital_by_companyId(self, company_id: str) -> dict:
        """
        Retrieves company data from the Capital database using the provided company ID.

        Args:
            company_id (str): The ID of the company to retrieve data for.

        Returns:
            dict: A dictionary containing the retrieved company data.
        """
        return self._find_row_by_companyId(OFFENREGISTER_CAPITAL_URL, company_id)

    def _find_from_Addresses_by_companyId(self, company_id: str) -> dict:
        """
        Retrieves the row from the Addresses table based on the given company ID.

        Args:
            company_id (str): The ID of the company.

        Returns:
            dict: The row from the Addresses table that matches the given company ID.
        """
        return self._find_row_by_companyId(OFFENREGISTER_ADDRESSES_URL, company_id)

    def _find_from_Objectives_by_companyId(self, company_id: str) -> dict:
        """
        Retrieves the row from Objectives by the given company ID.

        Args:
            company_id (str): The ID of the company.

        Returns:
            dict: The row containing the company data from Objectives.
        """
        return self._find_row_by_companyId(OFFENREGISTER_OBJECTIVES_URL, company_id)

    def _find_from_Names_by_companyId(self, company_id: str) -> dict:
        """
        Retrieves company data by company ID from the offerenregister.de website.

        Args:
            company_id (str): The ID of the company to retrieve data for.

        Returns:
            dict: A dictionary containing the retrieved company data.
        """
        return self._find_row_by_companyId(OFFENREGISTER_NAMES_URL, company_id)

    def find_companyName_by_lastName_firstName(self, last_name, first_name):
        """
        Finds the company name by the last name and first name of a person.

        Args:
            last_name (str): The last name of the person.
            first_name (str): The first name of the person.

        Returns:
            str: The name of the company if found, None otherwise.
        """
        pos_row = self._find_from_Positions_by_firstName_and_lastName(
            last_name, first_name
        )
        if pos_row:
            company_id = pos_row.get("col-companyId")
            name_row = self._find_from_Names_by_companyId(company_id)
            if name_row:
                return name_row.get("col-name")
            return None
        return None

    def find_companyCapitals_by_lastName_firstName(self, last_name, first_name):
        """
        Retrieves the capital amount and currency of a company based on the last name and first name of a person.

        Args:
            last_name (str): The last name of the person.
            first_name (str): The first name of the person.

        Returns:
            tuple: A tuple containing the capital amount and currency of the company. If the company or capital information is not found, returns (None, None).
        """
        pos_row = self._find_from_Positions_by_firstName_and_lastName(
            last_name, first_name
        )
        if pos_row:
            company_id = pos_row.get("col-companyId")
            capital_row = self._find_from_Capital_by_companyId(company_id)
            if capital_row:
                return capital_row.get("col-capitalAmount"), capital_row.get(
                    "col-capitalCurrency"
                )
            return None, None
        return None, None

    def find_companyObjective_by_lastName_firstName(self, last_name, first_name):
        """
        Finds the company objective based on the last name and first name of a person.

        Args:
            last_name (str): The last name of the person.
            first_name (str): The first name of the person.

        Returns:
            str or None: The company objective if found, None otherwise.
        """
        pos_row = self._find_from_Positions_by_firstName_and_lastName(
            last_name, first_name
        )
        if pos_row:
            company_id = pos_row.get("col-companyId")
            log.info(company_id)
            objective_row = self._find_from_Objectives_by_companyId(company_id)
            if objective_row:
                log.info(objective_row)
                return objective_row.get("col-objective")
            return None
        return None
