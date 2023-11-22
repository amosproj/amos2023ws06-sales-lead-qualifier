# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

from database import mongo_connection
from demos import bdc_demo, db_demo, evp_demo, pipeline_demo

if __name__ == "__main__":
    while True:
        try:
            choice = int(input("(1) BDC\n(2) EVP\n(3) DB\n(4) Pipeline\n(5) Exit\n"))
            match choice:
                case 1:
                    bdc_demo()
                case 2:
                    evp_demo()
                case 3:
                    db_demo()
                case 4:
                    pipeline_demo()
                case 5:
                    break
        except ValueError:
            print("Invalid choice")
