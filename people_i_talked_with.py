#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from zconf import get_zeo_key


# Variables ===================================================================
# Functions & classes =========================================================
def pick_unregistered(comments):
    return [
        not comment.registered
        for comment in comments
    ]


def i_was_the_poster(comment):
    if not comment.registered or not comment.username:
        return False

    return comment.username.lower() == "bystroushaak"


def people_i_talked_with(blogposts):
    for blog in blogposts.values():
        for comment in blog.comments:
            if i_was_the_poster(comment):
                previous = pick_unregistered(comment.response_to)
                responses = pick_unregistered(comment.responses)

                if responses:
                    yield responses

                if previous:
                    yield [previous]


# Main program ================================================================
if __name__ == '__main__':
    blogposts = get_zeo_key("blogposts")

    for cmnt in people_i_talked_with(blogposts):
        print cmnt.username, cmnt.url
