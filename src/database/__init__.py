# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

from .database_dummy import DatabaseDummy
from .db_connection import mongo_connection

_database = None


def get_database() -> DatabaseDummy:
    global _database
    if _database is None:
        _database = DatabaseDummy()
    return _database
