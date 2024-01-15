# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Berkay Bozkurt <resitberkaybozkurt@gmail.com>

import requests
from bs4 import BeautifulSoup
from deutschland.bundesanzeiger import Bundesanzeiger

from logger import get_logger

log = get_logger()

OFFENREGISTER_BASE_URL = "https://db.offeneregister.de/"
OFFENRENREGISTER_POSITION_URL = (
    OFFENREGISTER_BASE_URL
    + "openregister/Positions?firstName__contains={}&lastName__contains={}"
)


class CompanyDataRetriever:
    def __init__(self) -> None:
        pass

    def find_companyId_by_firstName_and_lastName(
        self, last_name: str, first_name: str
    ) -> str:
        url = OFFENRENREGISTER_POSITION_URL.format(first_name, last_name)
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

            # Find the first td element with class "col-companyId" within the first row
            col_companyId = first_row.find("td", {"class": "col-companyId"})
            # col_foundPosition = first_row.find('td', {'class': "col-foundPosition"})
            # Print the text within this td element
            return col_companyId.text
        else:
            print(f"Request failed with status code {response.status_code}")
            return None
