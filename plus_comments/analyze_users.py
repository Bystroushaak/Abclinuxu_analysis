#! /usr/bin/env python3
import re
import sys
import json
import gzip
from collections import defaultdict

import dhtmlparser


class User:
    PLUS_REGEXP = re.compile(r"\D\+1\D")
    MINUS_REGEXP = re.compile(r"\D\-1\D")

    def __init__(self, username=None):
        self.username = username
        self.counter = 0
        self.url_register = set()

    def _apply_blacklist(self, text):
        dom = dhtmlparser.parseString(text)

        blacklist = dom.find(
            "",
            fn=lambda x: x.getTagName() in [
                "i",
                "a",
                "bq",
                "pre",
                "italic",
                "blockquote",
            ]
        )

        for el in blacklist:
            el.replaceWith(dhtmlparser.parseString(""))

        return str(dom)

    def _decide(self, comment):
        text = self._apply_blacklist(comment["text"])

        if User.PLUS_REGEXP.search(text):
            return 1
        # elif User.MINUS_REGEXP.search(text):
        #     return -1

        return 0

    def process(self, comment_pair):
        val = self._decide(comment_pair["comment"])

        if val == 0:
            return

        self.counter += val
        self.username = comment_pair["response_to"]["username"]
        self.url_register.add(comment_pair["comment"]["url"])


def count_comments(comments):
    registered = defaultdict(User)
    unregistered = defaultdict(User)

    comment_n = len(comments)
    for cnt, comment_pair in enumerate(comments):
        print("%d/%d" % (cnt, comment_n), file=sys.stderr)

        comment = comment_pair["response_to"]
        if not comment:
            continue

        username = comment["username"].lower()
        if comment["registered"]:
            registered[username].process(comment_pair)
        else:
            unregistered[username].process(comment_pair)

    return registered, unregistered


def print_stats(dataset, title, registered=True, print_url=False):
    print("<h2>%s</h2>" % title)
    print("<p>")
    print("<ol>")

    for nick, user in sorted(dataset.items(), key=lambda x: x[-1].counter, reverse=True):
        if not user.username:
            user.username = nick

        if user.counter == 0:
            continue

        if registered:
            print(
                "<li><a href=\"http://abclinuxu.cz/lide/%s\">%s</a> (%s)" %
                (user.username, user.username, user.counter)
            )
        else:
            print(
                "<li><strong>%s</strong> (%s)" %
                (user.username, user.counter)
            )

        if print_url:
            for url in user.url_register:
                print("<ul><li><a href=\"%s\">%s</a></li></ul>" % (url, url))

        print("</li>")

    print("</ol>")
    print("</p>")


if __name__ == '__main__':
    with gzip.open("sign_comments.json.gz", "rt") as f:
        data = json.load(f)

    registered, unregistered = count_comments(data)

    print_stats(registered, "Registrovaní uživatelé")
    print_stats(unregistered, "Neregistrovaní uživatelé", False)
    print("<h1>Kontrolní výpis</h1>")
    print_stats(registered, "Registrovaní uživatelé", print_url=True)
    print_stats(unregistered, "Neregistrovaní uživatelé", False, True)

    # print(registered["gtz"].url_register)