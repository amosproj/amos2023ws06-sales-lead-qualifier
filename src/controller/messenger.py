# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Berkay Bozkurt <resitberkaybozkurt@gmail.com>

from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel


class MessageType(Enum):
    DATA = "data"
    PREDICTION = "prediction"


class SenderType(Enum):
    BDC = "base_data_collector"
    EVP = "estimated_value_predictor"


class Message(BaseModel):
    sender_name: SenderType
    data_type: MessageType
    data: Optional[Dict] = {}
    result: Optional[Dict] = {}


def create_data_message(lead_id, **features):
    """
    Creates a data message, called by BDC.
    """
    message = Message(
        sender_name=SenderType.BDC,
        data_type=MessageType.DATA,
        data={"lead_id": lead_id, **features},
    )
    return message


def create_prediction_message(lead_id, prediction_value):
    """
    Create a prediction message, called by EVP.
    """
    message = Message(
        sender_name=SenderType.EVP,
        data_type=MessageType.PREDICTION,
        result={"lead_id": lead_id, "prediction value": prediction_value},
    )
    return message
