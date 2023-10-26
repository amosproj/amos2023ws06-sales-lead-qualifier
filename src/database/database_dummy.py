# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

import json


class DatabaseDummy:
    def __init__(self) -> None:
        with open("src/database/dummy_leads.json") as f:
            json_data = json.load(f)["training_leads"]
            self.data = {d["lead_id"]: d for d in json_data}

    def get_entry_by_id(self, id_: int) -> dict:
        return self.data[id_]

    def get_all_entries(self):
        return self.data
