# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Sophie Heasman <sophieheasmann@gmail.com>

from abc import ABC, abstractmethod
from datetime import datetime


class Repository(ABC):
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    # Database paths for dataframe and reviews have to be set
    @property
    @abstractmethod
    def DF_INPUT(self):
        """
        Define database path to load dataframe
        """
        pass

    @property
    def DF_OUTPUT(self):
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

    @property
    @abstractmethod
    def SNAPSHOTS(self):
        """
        Define database path to store snapshots
        """
        pass

    @property
    @abstractmethod
    def GPT_RESULTS(self):
        """
        Define database path to store GPT operations
        """
        pass

    def __init__(self):
        """
        Initialise DAL, and saves the input df as an attribute
        :param download_df: Specify if you want to download the dataframe in this instance (not needed when handling reviews)
        """
        self.df = None
        self._download()

    def get_dataframe(self):
        return self.df

    def set_dataframe(self, df):
        self.df = df

    def get_input_path(self):
        return self.DF_INPUT

    def get_output_path(self):
        return self.DF_OUTPUT

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

    @abstractmethod
    def insert_data(self, data):
        """
        Insert new data into specified dataframe
        :param data: Data to be inserted (desired format must be checked)
        """
        pass

    @abstractmethod
    def create_snapshot(self, df, prefix, name):
        """
        Snapshot the current state of the dataframe
        :param df: Data to create a snapshot of
        :param prefix: Prefix for a group of snapshots belonging to a singe pipeline run, used to identify snapshots
        when cleaning up after a pipeline run
        :param name: Name of the snapshot
        :return: None
        """

    @abstractmethod
    def clean_snapshots(self, prefix):
        """
        Clean up the snapshots after a pipeline ran successfully
        :param prefix: Prefix of the current pipeline run used to identify all snapshots to delete
        """

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

    @abstractmethod
    def fetch_gpt_result(self, file_id, operation_name):
        """
        Fetches the GPT result for a given file ID and operation name.

        Args:
            file_id (str): The ID of the file.
            operation_name (str): The name of the GPT operation.

        Returns:
            The GPT result for the specified file ID and operation name.
        """
        pass

    @abstractmethod
    def save_gpt_result(self, gpt_result, file_id, operation_name, force_refresh=False):
        """
        Saves the GPT result for a given file ID and operation name.

        Args:
            gpt_result (str): The GPT result to be saved.
            file_id (str): The ID of the file.
            operation_name (str): The name of the operation.
            force_refresh (bool, optional): Whether to force a refresh of the saved result. Defaults to False.
        """
        pass

    def _get_current_time_as_string(self):
        """
        Get the current time as a string
        """
        return datetime.now().strftime(self.DATETIME_FORMAT)

    def _convert_string_time_to_datetime(self, time):
        """
        Convert a string time to a datetime object
        """
        return datetime.strptime(time, self.DATETIME_FORMAT)
