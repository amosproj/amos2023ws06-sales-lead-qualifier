# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

from config import DATABASE_TYPE
from logger import get_logger

from .database_dummy import DatabaseDummy
from .db_connection import mongo_connection
from .leads import LocalRepository, Repository, S3Repository

_database = None
log = get_logger()


def get_database() -> Repository:
    global _database
    if _database is None:
        if DATABASE_TYPE == "S3":
            log.debug("Using S3 database")
            _database = S3Repository()
        elif DATABASE_TYPE == "Local":
            log.debug("Using local database")
            _database = LocalRepository()
        else:
            log.error("Database type not initialised")
            raise ValueError

    return _database
