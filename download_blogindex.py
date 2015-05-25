#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import argparse

from abclinuxuapi import iter_blogposts
from abclinuxuapi import first_blog_page

from transaction import commit
from zconf import get_zeo_key


# Variables ===================================================================
# Functions & classes =========================================================
def main(everything=True, full_text=False):
    blogposts = get_zeo_key("blogposts")
    blog_urls = set(blogposts.keys())

    blog_getter = iter_blogposts if everything else first_blog_page

    for cnt, blog in enumerate(blog_getter()):
        print cnt + 1, blog.title

        if full_text:
            blog.pull()

        blogposts[blog.url] = blog

        if (cnt % 25) == 0:
            commit()

    commit()


# Main program ================================================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Download index of all published blogs."
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Download whole blogarchive, not just only first page."
    )
    parser.add_argument(
        "-f",
        "--full",
        action="store_true",
        help="Download full text of the blog and comments."
    )

    args = parser.parse_args()

    main(everything=args.all, full_text=args.full)
