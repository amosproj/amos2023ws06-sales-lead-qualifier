# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

from typing import List

import pandas as pd

from database.models import Lead
from database.parsers import LeadParser
from logger import get_logger

log = get_logger()


class DatabaseDummy:
    def __init__(self, input_file: str = "data/leads_enriched.csv") -> None:
        self.file = input_file
        self.leads = LeadParser.parse_leads_from_csv(self.file)

    def get_lead_by_id(self, id_: int) -> Lead:
        return self.leads[id_]

    def get_all_leads(self) -> List[Lead]:
        return self.leads

    def get_cardinality(self) -> int:
        return len(self.leads)

    def update_lead(self, lead: Lead):
        log.debug(f"Updating database entry for lead#{lead.lead_id}")
        log.debug(f"Update values: {lead}")
