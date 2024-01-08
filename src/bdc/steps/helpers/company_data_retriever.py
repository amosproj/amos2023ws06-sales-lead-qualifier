# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Berkay Bozkurt <resitberkaybozkurt@gmail.com>

from deutschland.bundesanzeiger import Bundesanzeiger

from logger import get_logger

log = get_logger()


class CompanyDataRetriever:
    def __init__(self) -> None:
        self.opencorporates_api_key = opencorporates_api_key
