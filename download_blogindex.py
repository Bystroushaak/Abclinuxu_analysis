#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
import argparse

from retrying import retry
from sqlitedict import SqliteDict
from timeout_wrapper import timeout

from abclinuxuapi import iter_blogposts
from abclinuxuapi import first_blog_page



@retry(stop_max_attempt_number=3, wait_fixed=20000)  # wait 20s
@timeout(120)
def pull(blog):
    blog.pull()


def download_blogtree(db_path, everything=True, full_text=False, uniq=False):
    blogpost_db = SqliteDict(db_path, autocommit=False)
    blog_getter = iter_blogposts if everything else first_blog_page

    already_downloaded = set(blogpost_db.keys())

    for cnt, blog in enumerate(blog_getter()):
        if uniq and blog.url in already_downloaded:
            print "skipping", blog.title
            continue

        print cnt + 1, blog.title

        if full_text:
            blog.pull()

        # don't save parsed HTML - this saves a LOT of space in database
        blog._dom = None
        blog._content_tag = None

        blogpost_db[blog.url] = blog

        if (cnt % 5) == 0:
            blogpost_db.commit()

    blogpost_db.commit()
    blogpost_db.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Download index of all published blogs."
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Download whole blogarchive, not just the first page."
    )
    parser.add_argument(
        "-f",
        "--full",
        action="store_true",
        help="Download full texts of the blog and comments."
    )
    parser.add_argument(
        "-u",
        "--uniq",
        action="store_true",
        help="Skip already downloaded items."
    )
    parser.add_argument(
        "PATH",
        help="Path to the SQLite file where the results will be stored."
    )

    args = parser.parse_args()

    download_blogtree(
        db_path=args.PATH,
        everything=args.all,
        full_text=args.full,
        uniq=args.uniq,
    )
