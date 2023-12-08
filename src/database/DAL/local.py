# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Sophie Heasman <sophieheasmann@gmail.com>

import pandas as pd

from database.DAL import DataAbstractionLayer
from logger import get_logger

log = get_logger()


class LocalDatabase(DataAbstractionLayer):
    DF = "./data/leads_enriched.csv"
    REVIEWS = "./data/reviews/"

    def _download(self):
        """
        Download database from specified DF path
        """
        try:
            self.df = pd.read_csv(self.DF)
        except FileNotFoundError:
            log.error("Error: Could not find input file for Pipeline.")

    def save_dataframe(self):
        """
        Save dataframe in df attribute in chosen output location
        """
        self.df.to_csv(self.DF, index=False)
        log.info(f"Saved enriched data locally to {self.DF}")

    def insert_data(self, data):
        """
        TODO: Insert new data into specified dataframe
        :param data: Data to be inserted (desired format must be checked)
        """
        pass

    def save_review(self, review):
        """
        TODO: Upload review to specified review path
        :param review: json contents of the review to be uploaded
        """
        pass

    def fetch_review(self, place_id):
        """
        TODO: Fetch review for specified place_id
        :return: json contents of desired review
        """
        pass
