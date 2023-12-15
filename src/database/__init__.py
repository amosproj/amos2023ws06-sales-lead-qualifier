# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

from config import DATABASE_TYPE
from database.DAL import DataAbstractionLayer, LocalDatabase, S3Database
from logger import get_logger

from .database_dummy import DatabaseDummy
from .db_connection import mongo_connection

_database = None
log = get_logger()


def get_database() -> DataAbstractionLayer:
    global _database
    if _database is None:
        if DATABASE_TYPE == "S3":
            _database = S3Database()
        elif DATABASE_TYPE == "Local":
            _database = LocalDatabase()
        else:
            log.error("Database type not initialised")
            raise ValueError

    return _database
