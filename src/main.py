# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

import os

from demo import (
    bdc_demo,
    db_demo,
    evp_demo,
    get_multiple_choice,
    pipeline_demo,
    preprocessing_demo,
)
from logger import get_logger

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

log = get_logger()

DEMOS = {
    "BDC": bdc_demo,
    "EVP": evp_demo,
    "DB": db_demo,
    "Pipeline": pipeline_demo,
    "Data preprocessing": preprocessing_demo,
}
PROMPT = "Choose demo:\n"

if __name__ == "__main__":
    options = list(DEMOS.keys()) + ["Exit"]
    while True:
        try:
            choice = get_multiple_choice(PROMPT, options)
            if choice == "Exit":
                break
            DEMOS[choice]()
        except ValueError:
            print("Invalid choice")
