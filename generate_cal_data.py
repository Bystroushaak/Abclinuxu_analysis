#! /usr/bin/env python2
# -*- coding: utf-8 -*-


"""
This script generates calendar data files like this::

    2019-05-28 1
    2019-05-19 1
    2019-05-05 1
    2019-04-18 1

for `termgraph tool <https://github.com/mkaz/termgraph>`_.

Example of usage::

    $ ./generate_cal_data.py blogtree.sqlite -o blogcal.tux.1.dat --tux
    $ termgraph --calendar --start-dt 2018-07-01 blogcal.tux.1.dat

              Jun Jul Aug Sep Oct Nov Dec Jan Feb Mar Apr May Jun
         Mon:                 ░  ░   ░░           ░
         Tue:            ░             ░    ░                 ░
         Wed:    ░  ░░             ░░ ░      ░ ░ ░ ▒
         Thu:   ░░             ░              ░    ░    ░
         Fri:     ▒          ░░ ░              ░
         Sat: ░       ░░              ░   ░  ▒░░
         Sun: ░    ░        ▒                  ░░         ░ ░
    $
"""


from __future__ import print_function
from collections import OrderedDict
from datetime import datetime
import argparse
import os
import sys
import urlparse

from sqlitedict import SqliteDict


# TODO: add into Blogpost class?
def get_blogname(url):
    return urlparse.urlparse(url).path.split("/")[2]


def get_cal_blogs_per_day(serialized, blogname, filter_tux, out_file):
    number_of_blogs_per_day = OrderedDict()
    for blog in serialized.itervalues():
        date = datetime.fromtimestamp(blog.created_ts).strftime('%Y-%m-%d')
        name = get_blogname(blog.url)
        if blogname is not None and name != blogname:
            continue
        if filter_tux is not None:
            if filter_tux and not blog.has_tux:
                continue
            if not filter_tux and blog.has_tux:
                continue
        number_of_blogs_per_day.setdefault(date, 0)
        number_of_blogs_per_day[date] += 1
    for date, count in number_of_blogs_per_day.iteritems():
        print(date, count, file=out_file)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(
        description="generate termgraph cal data file")
    ap.add_argument(
        "blogtree",
        metavar="BLOGTREE.sqlite",
        help="Path to the blogtree .sqlite file.")
    ap.add_argument(
        "-o",
        "--output",
        nargs='?',
        type=argparse.FileType('w'),
        default=sys.stdout,
        help=("Name of the output file."
              "Data are printed to stdout if not specified."))
    ap.add_argument(
        "--blogname",
        help="Process only blogposts in given blog.")
    ap.add_argument(
        "--tux",
        dest="tux",
        action="store_true",
        help="Process only blogposts with tux.")
    ap.add_argument(
        "--no-tux",
        dest="tux",
        action="store_false",
        help="Process only blogposts without tux.")
    args = ap.parse_args()

    if not os.path.exists(args.blogtree):
        sys.stderr.write("`%s` not found.\n" % args.blogtree)
        sys.exit(1)

    with SqliteDict(args.blogtree) as serialized:
        get_cal_blogs_per_day(
            serialized,
            args.blogname,
            args.tux,
            args.output)
