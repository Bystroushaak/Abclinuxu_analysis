#! /usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
import argparse

from tqdm import tqdm
from sqlitedict import SqliteDict


def pick_correct_poster(comment, username, registered):
    if registered and not comment.registered:
        return False

    if not comment.username:
        return False

    return comment.username.lower() == username


def grep_in_blog(blog, username, registered, strings, case_sensitive):
    for comment in blog.comments:
        if not pick_correct_poster(comment, username, registered):
            continue

        if case_sensitive:
            blog_text = comment.text
        else:
            blog_text = comment.text.lower()

        def maybe_lower(s):
            if case_sensitive:
                return s
            
            return s.lower()

        if all(maybe_lower(string) in blog_text for string in strings):
            print comment.url
            print comment.text
            print
            print


def grep_in_blogtree(blogtree_path, username, registered, string, case_sensitive):
    with SqliteDict(blogtree_path) as serialized:
        for blog in tqdm(serialized.itervalues(), total=len(serialized)):
            grep_in_blog(blog, username, registered, string, case_sensitive)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-b",
        "--blogtree",
        required=True,
        metavar="BLOGTREE.sqlite",
        help="Path to the blogtree .sqlite file."
    )
    parser.add_argument(
        "-c",
        "--case-sensitive",
        action="store_true",
        help="Grep `string` case sensitively."
    )
    parser.add_argument(
        "-r",
        "--registered",
        action="store_true",
        help="User must be registered."
    )
    parser.add_argument(
        "-u",
        "--username",
        required=True,
        help="Username to grep."
    )
    parser.add_argument(
        "strings",
        nargs="+",
        help="String to grep in blogtree."
    )
    args = parser.parse_args()

    grep_in_blogtree(
        args.blogtree,
        args.username,
        args.registered,
        args.strings,
        args.case_sensitive,
    )
