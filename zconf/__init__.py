#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os.path

import ZODB.config
from ZODB import DB
from persistent.mapping import PersistentMapping


# Variables ===================================================================
PROJECT_KEY = "abclinuxu"


# Functions & classes =========================================================
def get_zeo_connection():
    path = os.path.join(os.path.dirname(__file__), "zeo_client.conf")

    db = DB(
        ZODB.config.storageFromFile(open(path))
    )
    return db.open()


def get_zeo_root():
    conn = get_zeo_connection()
    dbroot = conn.root()

    if PROJECT_KEY not in dbroot:
        from BTrees.OOBTree import OOBTree
        dbroot[PROJECT_KEY] = OOBTree()

    return dbroot[PROJECT_KEY]


def get_zeo_key(key, new_obj=PersistentMapping):
    root = get_zeo_root()

    if not root.get(key, None):
        root[key] = new_obj()

    return root[key]
