# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Ruchita Nathani <ruchita.nathani@fau.de>

from bdc.data_collector import DataCollector

dc = DataCollector()
dc.get_data_from_csv()
print("Successfully Get Data From the CSV File")

dc.get_data_from_api()
print("Successfully Get Data From the API and stored in JSOn file at 'src/data/collected_data.json'")
