# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from database import DatabaseDummy


def get_database_mock():
    return DatabaseDummy("tests/test_data/database_dummies.csv")
