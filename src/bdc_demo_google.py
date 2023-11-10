# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Ruchita Nathani <ruchita.nathani@fau.de>

from bdc.data_collector import DataCollector

dc = DataCollector()
dc.get_data_from_csv()
dc.get_data_from_google_api()
