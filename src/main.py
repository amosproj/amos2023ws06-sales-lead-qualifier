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
    "Estimated Value Predictor": evp_demo,
    "Merchant Size Prediction": predict_MerchantSize_on_lead_data_demo,
}
PROMPT = "Choose demo:\n"

EXIT = "Exit"

if __name__ == "__main__":
    options = list(DEMOS.keys()) + [EXIT]
    while True:
        try:
            choice = get_multiple_choice(PROMPT, options)
            if choice == EXIT:
                break
            DEMOS[choice]()
        except ValueError:
            print("Invalid choice")
