# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Ruchita Nathani <ruchita.nathani@fau.de>

import requests
import json

api_url = "https://dummyjson.com/products/1"

response = requests.get(api_url)

if response.status_code == 200:
    data = response.json()

    with open("../data/collected_data.json", "w") as json_file:
        json.dump(data, json_file, indent=4)
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")
