# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Sophie Heasman <sophieheasmann@gmail.com>

from abc import ABC, abstractmethod


class DataAbstractionLayer(ABC):
    # Database paths for dataframe and reviews have to be set
    @property
    @abstractmethod
    def DF(self):
        """
        Define database path to store dataframe
        """
        pass

    @property
    @abstractmethod
    def REVIEWS(self):
        """
        Define database path to store reviews
        """
        pass

    def __init__(self, download_df=True):
        """
        Initialise DAL, and saves the input df as an attribute
        :param download_df: Specify if you want to download the dataframe in this instance (not needed when handling reviews)
        """
        self.df = None

        if download_df:
            self._download()

    @abstractmethod
    def _download(self):
        """
        Download database from specified DF path
        """
        pass

    @abstractmethod
    def save_dataframe(self):
        """
        Save dataframe in df attribute in chosen output location
        """
        pass

    def get_dataframe(self):
        return self.df

    def set_dataframe(self, df):
        self.df = df

    @abstractmethod
    def insert_data(self, data):
        """
        Insert new data into specified dataframe
        :param data: Data to be inserted (desired format must be checked)
        """
        pass

    @abstractmethod
    def save_review(self, review, place_id, force_refresh=False):
        """
        Upload review to specified review path
        :param review: json contents of the review to be uploaded
        """
        pass

    @abstractmethod
    def fetch_review(self, place_id):
        """
        Fetch review for specified place_id
        :return: json contents of desired review
        """
        pass
