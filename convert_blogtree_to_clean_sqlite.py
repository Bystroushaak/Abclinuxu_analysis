#! /usr/bin/env python2
# -*- coding: utf-8 -*-
import sys
import os.path
import sqlite3
import argparse

from tqdm import tqdm
from sqlitedict import SqliteDict


def create_tables(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `Blogs` (
            `url` TEXT UNIQUE,
            `id` INTEGER UNIQUE,
            `title` TEXT,
            `perex` TEXT,
            `content` TEXT,
            `rating` INTEGER,
            `rating_base` INTEGER,
            `has_tux` INTEGER DEFAULT 0,
            `number_of_reads` INTEGER DEFAULT 0,
            `downloaded_ts` INTEGER,
            `created_ts` INTEGER,
            `last_modified_ts` INTEGER,
            PRIMARY KEY(`url`,`id`)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "Comments" (
            `id` INTEGER PRIMARY KEY AUTOINCREMENT,
            `url` TEXT,
            `content` TEXT,
            `timestamp` INTEGER,
            `username` TEXT,
            `user_registered` INTEGER,
            `censored` INTEGER
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "Tags" (
            `id` TEXT UNIQUE,
            `tag` TEXT,
            PRIMARY KEY(`id`)
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `blog_has_comment` (
            `blog_id` INTEGER,
            `comment_id` INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "blog_has_tag" (
            `blog_id` INTEGER,
            `tag_id` INTEGER
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `comment_has_responses` (
            `comment_id` INTEGER,
            `response_id` INTEGER
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `comment_responds_to` (
            `comment_id` INTEGER,
            `parent_id` INTEGER DEFAULT 0
        );
    """)


def serialize_tags(cursor, blog):
    for tag in blog.tags:
        cursor.execute(
            "INSERT OR IGNORE INTO Tags VALUES (?, ?)",
            (tag.norm, tag.tag)
        )
        cursor.execute(
            "INSERT INTO blog_has_tag VALUES (?, ?)",
            (blog.uid, tag.norm)
        )


def _comment_str_id_to_numeric(blog, comment):
    return blog.uid * 1000000 + int(comment.id)


def serialize_comments(cursor, blog):
    for comment in blog.comments:
        comment_id = _comment_str_id_to_numeric(blog, comment)
        cursor.execute(
            """INSERT OR IGNORE INTO Comments VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                comment_id,
                comment.url,
                comment.text,
                comment.timestamp,
                comment.username,
                comment.registered,
                comment.censored,
            )
        )
        cursor.execute(
            "INSERT INTO blog_has_comment VALUES (?, ?)",
            (blog.uid, comment_id)
        )
        if comment.response_to:
            cursor.execute(
                "INSERT INTO comment_responds_to VALUES (?, ?)",
                (comment_id, _comment_str_id_to_numeric(blog, comment.response_to))
            )
        
        for response in comment.responses:
            cursor.execute(
                "INSERT OR IGNORE INTO comment_has_responses VALUES (?, ?)",
                (comment_id, _comment_str_id_to_numeric(blog, response))
            )


def serialize_blogpost(cursor, blog):
    cursor.execute(
        """INSERT INTO Blogs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            blog.relative_url,
            blog.uid,
            blog.title,
            blog.intro,
            blog.text,
            blog.rating.rating if blog.rating else 0,
            blog.rating.base if blog.rating else 0,
            blog.has_tux,
            blog.readed,
            blog.object_ts,
            blog.created_ts,
            blog.last_modified_ts,
        )
    )

    serialize_tags(cursor, blog)
    serialize_comments(cursor, blog)


def convert_blogtree(blogtree_path, output_path):
    conn = sqlite3.connect(output_path)
    conn.text_factory = str
    cursor = conn.cursor()

    create_tables(cursor)
    conn.commit()

    with SqliteDict(blogtree_path) as serialized:
        for blog in tqdm(serialized.itervalues(), total=len(serialized)):
            serialize_blogpost(cursor, blog)
            conn.commit()
    
    conn.commit()


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
        default="blogtree_clean.sqlite",
        help="Name of the output file. Default `%(default)s.`",
    )

    args = parser.parse_args()

    if not os.path.exists(args.blogtree):
        sys.stderr.write("`%s` not found.\n" % args.blogtree)
        sys.exit(1)

    convert_blogtree(args.blogtree, args.output)
