#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from transaction import commit
from BTrees.OOBTree import OOBTree

from zconf import get_zeo_key

from download_blogindex import pull


# Variables ===================================================================
# Functions & classes =========================================================
def main():
    blogposts = get_zeo_key("blogposts", OOBTree)

    for blog in blogposts.values():
        if blog.text is None:
            print blog.url

            pull(blog)
            blog._dom = None
            blog._content_tag = None

            blogposts._p_changed = True
            blogposts[blog.url] = blog
            commit()

    commit()


# Main program ================================================================
if __name__ == '__main__':
    main()
