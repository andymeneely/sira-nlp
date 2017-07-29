"""
@AUTHOR: nuthanmunaiah
"""
import multiprocessing
import sys

import pandas
from django.db import connection, Error, transaction

from app.queryStrings import is_familiar_with_bug
from app.lib.helpers import get_project_experience, \
                            get_module_experience,  \
                            get_file_experience
from app.lib.taggers import tagger
from app.lib.utils import parallel
from app.models import *

REVIEWS = None
COMMENTS = None


def aggregate(oqueue, cqueue, num_doers):
    count, done = 0, 0
    while True:
        item = cqueue.get()
        if item == parallel.DD:
            done += 1
            if done == num_doers:
                break  # All doers are done
            continue  # pragma: no cover

        comment = item
        try:
            with transaction.atomic():
                comment.save()
                count += 1
        except Error as err:  # pragma: no cover
            sys.stderr.write('Exception\n')
            sys.stderr.write('  Comment  {}\n'.format(comment.id))
            extype, exvalue, extrace = sys.exc_info()
            traceback.print_exception(extype, exvalue, extrace)
    oqueue.put(count)


def do(iqueue, cqueue):  # pragma: no cover
    while True:
        item = iqueue.get()
        if item == parallel.EOI:
            cqueue.put(parallel.DD)
            break

        comment = item

        if 'experience' not in comment.metrics:
            comment.metrics['experience'] = dict()

        # Filters
        reviews = REVIEWS[REVIEWS.created < comment.posted]
        comments = COMMENTS[COMMENTS.posted < comment.posted]

        experience = get_project_experience(comment, reviews, comments)
        comment.metrics['experience']['project'] = experience
        experience = get_module_experience(comment, reviews, comments)
        comment.metrics['experience']['module'] = experience
        experience = get_file_experience(comment, reviews, comments)
        comment.metrics['experience']['file'] = experience
        experience = is_familiar_with_bug(comment)
        comment.metrics['experience']['bug'] = experience

        cqueue.put(comment)


def stream(comments, iqueue, num_doers):
    for comment in comments:
        iqueue.put(comment)

    for i in range(num_doers):
        iqueue.put(parallel.EOI)


class ExperienceTagger(tagger.Tagger):
    def __init__(self, settings, num_processes, comments):
        super(ExperienceTagger, self).__init__(settings, num_processes)
        self.comments = comments

    def tag(self):
        self._init_globals()

        iqueue = parallel.manager.Queue(self.settings.QUEUE_SIZE)

        process = self._start_streaming(iqueue)
        count = parallel.run(do, aggregate, iqueue, self.num_processes)
        process.join()

        return count

    def _init_globals(self):
        global REVIEWS, COMMENTS

        # Reviews
        query = '''
            SELECT r.id AS id,
                r.created AS created,
                r.document -> 'reviewers' AS reviewers,
                r.document -> 'reviewed_files' AS reviewed_files,
                r.document -> 'reviewed_modules' AS reviewed_modules,
                jsonb_array_length(r.document -> 'reviewers') AS num_reviewers
            FROM review r
        '''
        REVIEWS = pandas.read_sql(query, connection)

        query = '''
            SELECT c.id AS id,
                c.author AS author,
                c.posted AS posted,
                c.by_reviewer AS by_reviewer,
                p.file_path AS file_path,
                p.module_path AS module_path,
                ps.review_id AS review_id
            FROM comment c
                JOIN patch p ON p._id = c.patch_id
                JOIN patchset ps ON ps._id = p.patchset_id
            WHERE c.by_reviewer IS true;
        '''
        COMMENTS = pandas.read_sql(query, connection)

    def _start_streaming(self, iqueue):
        process = multiprocessing.Process(
                target=stream, args=(self.comments, iqueue, self.num_processes)
            )
        process.start()

        return process
