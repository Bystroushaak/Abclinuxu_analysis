#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
import sys
import argparse
from Queue import Empty
from multiprocessing import Queue
from multiprocessing import Process

from retrying import retry
from sqlitedict import SqliteDict
from timeout_wrapper import timeout

from abclinuxuapi import iter_blogposts
from abclinuxuapi import first_blog_page
from abclinuxuapi import number_of_blog_pages


class WorkerDone(object):
    pass


def sqlitedict_writer(db_path, no_blogs, number_of_downloaders, blog_queue):
    circuit_breaker = 0
    number_of_active_downloaders = number_of_downloaders

    with SqliteDict(db_path, autocommit=False) as blogpost_db:
        for cnt in xrange(100000000):
            try:
                blog = blog_queue.get(block=True, timeout=5)
            except Empty:
                circuit_breaker += 1
                if circuit_breaker > 5:
                    break
                continue

            if isinstance(blog, WorkerDone):
                number_of_active_downloaders -= 1
            if number_of_active_downloaders == 0:
                break

            blogpost_db[blog.url] = blog
            print cnt + 1, no_blogs, blog.title

            if (cnt % 5) == 0:
                blogpost_db.commit()

        blogpost_db.commit()


@retry(stop_max_attempt_number=3, wait_fixed=20000)  # wait 20s
@timeout(120)
def pull(blog):
    blog.pull()

    # don't save parsed HTML - this saves a LOT of space in database
    blog._dom = None
    blog._content_tag = None


def blog_downloader(in_queue, writer_queue):
    while True:
        try:
            blog = in_queue.get(block=True, timeout=5)
        except Empty:
            # wait for more urls
            continue

        if isinstance(blog, WorkerDone):
            writer_queue.put(WorkerDone())
            break

        pull(blog)
        writer_queue.put(blog)


def get_number_of_blogs():
    print "Estimating number of blogs..",

    def print_progress(n):
        sys.stdout.write(".")
        sys.stdout.flush()

    no_blogs = "/ ~%d" % (number_of_blog_pages(print_progress) * 25)

    print

    return no_blogs


def download_blogtree(db_path, everything=True, full_text=False, uniq=False,
                      number_of_downloaders=4):
    blog_getter = iter_blogposts if everything else first_blog_page

    with SqliteDict(db_path, autocommit=False) as blogpost_db:
        already_downloaded = set(blogpost_db.keys())

    no_blogs = get_number_of_blogs() if everything else ""

    empty_blog_queue = Queue()
    sqlite_writer_queue = Queue()
    writer = Process(
        target=sqlitedict_writer,
        args=(db_path, no_blogs, number_of_downloaders, sqlite_writer_queue)
    )
    writer.start()
    workers = [
        Process(
            target=blog_downloader,
            args=(empty_blog_queue, sqlite_writer_queue)
        )
        for _ in range(number_of_downloaders)
    ]
    for worker in workers:
        worker.start()

    for cnt, blog in enumerate(blog_getter()):
        if uniq and blog.url in already_downloaded:
            print "skipping", cnt + 1, blog.title
            continue

        empty_blog_queue.put(blog)

    # put signals for workers that job is done
    for _ in range(number_of_downloaders):
        empty_blog_queue.put(WorkerDone())

    # wait for workers
    for worker in workers:
        worker.join()

    # wait for writer
    writer.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Download all published blogs on abclinuxu.cz."
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
        "-w",
        "--workers",
        default=8,
        type=int,
        help="Number of workers. Default %(default)s."
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
        number_of_downloaders=args.workers,
    )
