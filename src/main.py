# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

import os

from demos import bdc_demo, db_demo, evp_demo, pipeline_demo, preprocessing_demo
from logger import get_logger

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

log = get_logger()

if __name__ == "__main__":
    while True:
        try:
            choice = int(
                input(
                    "(1) BDC\n(2) EVP\n(3) DB\n(4) Pipeline\n(5) Data preprocessing\n(6) Exit\n"
                )
            )
            match choice:
                case 1:
                    bdc_demo()
                case 2:
                    # TODO: adjust demo with new way of training the models
                    evp_demo()
                case 3:
                    db_demo()
                case 4:
                    pipeline_demo()
                case 5:
                    preprocessing_demo()
                case 6:
                    break
        except ValueError:
            print("Invalid choice")
