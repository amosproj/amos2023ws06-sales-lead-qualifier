# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Ruchita Nathani <ruchita.nathani@fau.de>

import pymongo

from config import DB_CONNECTION

_client = None


def mongo_connection(collection_name="default"):
    global _client
    if _client is None:
        _client = pymongo.MongoClient(DB_CONNECTION)
    db = _client["leads_enriched"]
    collection = db[collection_name]
    return collection
