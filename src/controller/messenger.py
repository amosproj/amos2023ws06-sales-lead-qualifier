# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Berkay Bozkurt <resitberkaybozkurt@gmail.com>

from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel


class MessageType(Enum):
    DATA = "data"
    PREDICTION = "prediction"


class Message(BaseModel):
    sender_name: str
    data_type: str
    data: Optional[Dict] = {}
    result: Optional[Dict] = {}


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
