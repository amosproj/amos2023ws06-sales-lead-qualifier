# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

import os

from demo import (
    evp_demo,
    get_multiple_choice,
    pipeline_demo,
    predict_MerchantSize_on_lead_data_demo,
    preprocessing_demo,
)
from logger import get_logger

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

log = get_logger()

DEMOS = {
    "Base Data Collector": pipeline_demo,
    "Data preprocessing": preprocessing_demo,
    "ML model training": evp_demo,
    "Merchant Size Predictor": predict_MerchantSize_on_lead_data_demo,
}
PROMPT = "Choose demo:\n"

EXIT = "Exit"

if __name__ == "__main__":
    options = list(DEMOS.keys()) + [EXIT]
    while True:
        choice = get_multiple_choice(PROMPT, options)
        if choice == EXIT:
            break
        if choice != None:
            DEMOS[choice]()
