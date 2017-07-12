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

PATTERN = re.compile(r'>\s([^\n]*)\n\n')

def _get_aggregate(comments):
    aggregate = dict()
    for comment in comments:
        if comment.patch.path not in aggregate:
            aggregate[comment.patch.path] = dict()
        if comment.line not in aggregate[comment.patch.path]:
            aggregate[comment.patch.path][comment.line] = list()
        aggregate[comment.patch.path][comment.line].append(comment)
    return aggregate


def aggregate(oqueue, cqueue, num_doers):
    count, done = 0, 0
    while True:
        item = cqueue.get()
        if item == parallel.DD:
            done += 1
            if done == num_doers:
                break
            continue # pragma: no cover
        count += item
    oqueue.put(count)


def do(iqueue, cqueue): # pragma: no cover
    while True:
        item = iqueue.get()
        if item == parallel.EOI:
            cqueue.put(parallel.DD)
            break

        (path, lines) = item
        cnt = 0
        with transaction.atomic():
            try:
                for line in lines:
                    for comment in lines[line]:
                        #print(comment.to_dict())
                        if comment.by_reviewer == False and \
                            comment.text.startswith("\nDone."):
                            if comment.parent is not None:
                                comment.parent.is_useful = True
                                comment.parent.save()
                                cnt += 1
                            else:
                                print(comment.to_dict())

            except Error as err: # pragma: no cover
                sys.stderr.write('Exception\n')
                sys.stderr.write('  Path  {}\n'.format(path))
                extype, exvalue, extrace = sys.exc_info()
                traceback.print_exception(extype, exvalue, extrace)

        cqueue.put(cnt)


def stream(review_ids, iqueue, num_doers):
    for review_id in review_ids:
        review = Review.objects.filter(id=review_id)
        comments = Comment.objects.filter(patch__patchset__review=review) \
                                  .order_by('patch__path', 'line', 'posted')
        for (path, lines) in _get_aggregate(comments).items():
            iqueue.put((path, lines))

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
