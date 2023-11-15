# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

import json
from typing import List

from database.models import Lead
from database.parsers import LeadParser


class DatabaseDummy:
    def __init__(self, input_file: str = "src/data/collected_data.json") -> None:
        try:
            with open(input_file) as f:
                json_data = json.load(f)
                self.data = {d["lead_id"]: d for d in json_data}
        except FileNotFoundError as e:
            print(
                f"Error: Database dummy file {input_file} not found. Try running the BDC first"
            )
            self.data = {}

    def get_lead_by_id(self, id_: int) -> Lead:
        return LeadParser.parse_lead_from_dict(self.data[id_])

    def get_all_leads(self) -> List[Lead]:
        return [LeadParser.parse_lead_from_dict(entry) for entry in self.data.values()]

    def get_cardinality(self) -> int:
        return len(self.data)

    def update_lead(self, lead: Lead):
        print(f"Updating database entry for lead#{lead.lead_id}")
        print(f"Update values: {lead}")
