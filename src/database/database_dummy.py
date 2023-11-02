# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

import json
from typing import List

from database.models import Lead
from database.parsers import LeadParser


class DatabaseDummy:
    def __init__(self) -> None:
        with open("src/database/dummy_leads.json") as f:
            json_data = json.load(f)["training_leads"]
            self.data = {d["lead_id"]: d for d in json_data}

    def get_lead_by_id(self, id_: int) -> Lead:
        return LeadParser.parse_lead_from_dict(self.data[id_])

    def get_all_leads(self) -> List[Lead]:
        leads = []
        for entry in self.data.values():
            leads.append(LeadParser.parse_lead_from_dict(entry))
        return leads

    def update_lead(self, lead: Lead):
        print(f"Updating database entry for lead#{lead.lead_id}")
        print(f"Update values: {lead}")
