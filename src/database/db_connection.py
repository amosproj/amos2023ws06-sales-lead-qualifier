# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Ruchita Nathani <ruchita.nathani@fau.de>

import pymongo


def mongo_connection(collection_name="default"):
    client = pymongo.MongoClient("mongodb://root:example@localhost:27017/")
    db = client["leads_enriched"]
    collection = db[collection_name]
    return collection
