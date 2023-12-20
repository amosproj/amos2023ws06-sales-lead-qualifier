# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

from database import DatabaseDummy


def get_database_mock():
    return DatabaseDummy("tests/test_data/database_dummies.csv")
