#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os.path
import sqlite3
import argparse

from tqdm import tqdm
from sqlitedict import SqliteDict


def create_tables(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `edges` (
            `source` INTEGER,
            `target` INTEGER
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `nodes` (
            `id` INTEGER,
            `label` TEXT,
            PRIMARY KEY(`id`)
        )
    """)


def username_from_comment(comment):
    return comment.username if comment.registered else comment.username + " (unregisted)"


def process_blogpost(blog, users, talks_to):
    for comment in blog.comments:
        username = username_from_comment(comment)
        users.add(username)

        if comment.response_to:
            talks_to[username] = username_from_comment(comment.response_to)


def generate_gephi_sqlite(blogtree_path, output_path):
    conn = sqlite3.connect(output_path)
    conn.text_factory = str
    cursor = conn.cursor()

    create_tables(cursor)
    conn.commit()

    users = set()
    talks_to = {}

    with SqliteDict(blogtree_path) as serialized:
        for blog in tqdm(serialized.itervalues(), total=len(serialized)):
            process_blogpost(blog, users, talks_to)
            conn.commit()

    user_to_id = {}
    for cnt, username in enumerate(list(users)):
        user_to_id[username] = cnt

    for user, uid in tqdm(user_to_id.iteritems(), total=len(user_to_id)):
        cursor.execute(
            "INSERT INTO nodes VALUES (?, ?)",
            (uid, user)
        )

    conn.commit()

    for who, to in tqdm(talks_to.iteritems(), total=len(talks_to)):
        cursor.execute(
            "INSERT INTO edges VALUES (?, ?)",
            (user_to_id[who], user_to_id[to])
        )

    conn.commit()
    conn.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "blogtree",
        metavar="BLOGTREE.sqlite",
        help="Path to the blogtree .sqlite file."
    )
    parser.add_argument(
        "-o",
        "--output",
        default="gephi.sqlite",
        help="Name of the output file. Default `%(default)s.`",
    )

    args = parser.parse_args()

    if not os.path.exists(args.blogtree):
        sys.stderr.write("`%s` not found.\n" % args.blogtree)
        sys.exit(1)

    generate_gephi_sqlite(args.blogtree, args.output)
