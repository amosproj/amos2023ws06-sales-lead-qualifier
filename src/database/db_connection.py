# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Ruchita Nathani <ruchita.nathani@fau.de>

import pymongo

_client = None


def mongo_connection(collection_name="default"):
    global _client
    if _client is None:
        _client = pymongo.MongoClient("mongodb://root:example@mongodb:27017/")
    db = _client["leads_enriched"]
    collection = db[collection_name]
    return collection
