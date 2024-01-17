# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

import os

from bdc.steps.helpers.offeneregister_api import CompanyDataRetriever
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

EXIT = "Exit"

if __name__ == "__main__":
    cdp = CompanyDataRetriever()
    # name = cdp.find_companyName_by_lastName_firstName("Souissi", "Rim")
    obj = cdp.find_companyObjective_by_lastName_firstName("Souissi", "Rim")
    log.info(obj)
    options = list(DEMOS.keys()) + [EXIT]
    while True:
        try:
            choice = get_multiple_choice(PROMPT, options)
            if choice == EXIT:
                break
            DEMOS[choice]()
        except ValueError:
            print("Invalid choice")
