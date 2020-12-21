#! /usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import re
import sys
import json

from zconf import get_zeo_key


# Variables ===================================================================
PLUS_REGEXP = re.compile(r"\+[0-9]")
MINUS_REGEXP = re.compile(r"\-[0-9]")


# Functions & classes =========================================================
def is_plus_comment(comment):
    return bool(PLUS_REGEXP.search(comment.text))


def is_minus_comment(comment):
    return bool(MINUS_REGEXP.search(comment.text))


def pick_plus_comments(blogposts):
    for blog in blogposts.values():
        for comment in blog.comments:
            if is_plus_comment(comment) or is_minus_comment(comment):
                yield comment


def serialize_comment(comment):
    def to_dict(comment):
        return {
            "url": comment.url,
            "text": comment.text,
            "timestamp": comment.timestamp,
            "username": comment.username,
            "registered": comment.registered,
        }

    response_to = to_dict(comment.response_to) if comment.response_to else None

    return {
        "comment": to_dict(comment),
        "response_to": response_to,
    }


# Main program ================================================================
if __name__ == '__main__':
    blogposts = get_zeo_key("blogposts")

    result = [
        serialize_comment(plus_comment)
        for plus_comment in pick_plus_comments(blogposts)
    ]

    json.dump(
        obj=result,
        fp=sys.stdout,
        indent=4,
        separators=(',', ': '),
    )
