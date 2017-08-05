import multiprocessing
import re
import sys
import traceback

from django.db import Error, transaction
from django.db.models import Q

from app.lib import taggers, logger
from app.lib.nlp import analyzers
from app.lib.utils import parallel
from app.models import *


PATTERN = r'^\nDone\.'


def aggregate(oqueue, cqueue, num_doers):
    count, done = 0, 0
    while True:
        item = cqueue.get()
        if item == parallel.DD:
            done += 1
            if done == num_doers:
                break
            continue  # pragma: no cover
        count += item
    oqueue.put(count)


def do(iqueue, cqueue):  # pragma: no cover
    while True:
        item = iqueue.get()
        if item == parallel.EOI:
            cqueue.put(parallel.DD)
            break

        comment = item
        cnt = 0
        with transaction.atomic():
            try:
                if comment.parent is not None:
                    if comment.parent.by_reviewer is True:
                        # Parent of the change-indicating comment is a comment
                        # posted by a reviewer. Tag it as useful.
                        comment.parent.is_useful = True
                        comment.parent.save()
                    else:
                        # Parent of the change-indicating comment is a comment
                        # not posted by a reviewer. Traverse the comment thread
                        # until a comment posted by a reviewer is found or no
                        # more comments remain.
                        parent = comment.parent
                        while parent is not None and not parent.by_reviewer:
                            parent = parent.parent
                        if parent is not None:
                            parent.is_useful = True
                            parent.save()
                cnt += 1
            except Error as err:  # pragma: no cover
                sys.stderr.write('Exception\n')
                sys.stderr.write('  Comment  {}\n'.format(comment.id))
                extype, exvalue, extrace = sys.exc_info()
                traceback.print_exception(extype, exvalue, extrace)

        cqueue.put(cnt)


def stream(review_ids, iqueue, num_doers):
    comments = Comment.objects                                           \
                      .filter(patch__patchset__review_id__in=review_ids) \
                      .filter(by_reviewer=False, text__regex=PATTERN)    \
                      .order_by('patch__file_path', 'line', 'posted')

    for comment in comments:
        iqueue.put(comment)

    for i in range(num_doers):
        iqueue.put(parallel.EOI)


class UsefulCommentTagger(taggers.Tagger):
    def __init__(self, settings, num_processes, review_ids):
        super(UsefulCommentTagger, self).__init__(settings, num_processes)
        self.review_ids = review_ids

    def tag(self):
        iqueue = parallel.manager.Queue(self.settings.QUEUE_SIZE)

        process = self._start_streaming(iqueue)
        count = parallel.run(do, aggregate, iqueue, self.num_processes)
        process.join()

        return count

    def _start_streaming(self, iqueue):
        process = multiprocessing.Process(
                target=stream,
                args=(self.review_ids, iqueue, self.num_processes)
            )
        process.start()

        return process
