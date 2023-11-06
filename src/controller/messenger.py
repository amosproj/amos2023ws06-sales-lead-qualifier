# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Berkay Bozkurt <resitberkaybozkurt@gmail.com>

from enum import Enum


class MessageType(Enum):
    DATA = "data"
    PREDICTION = "prediction"


class Message:
    def __init__(self, sender_name, data_type, data=None, result=None):
        self.sender_name = sender_name
        self.data_type = data_type
        self.data = data if data is not None else {}
        self.result = result if result is not None else {}


def create_data_message(lead_id, **features):
    """
    Creates a data message, called by BDC.
    """
    message = Message("BDC", MessageType.DATA, {"lead_id": lead_id, **features})
    return message


def create_prediction_message(lead_id, prediction_value):
    """
    Create a prediction message, called by EVP.
    """
    message = Message(
        "EVP",
        MessageType.PREDICTION,
        result={"lead_id": lead_id, "prediction value": prediction_value},
    )
    return message
