import multiprocessing
import re
import sys
import traceback

from django.db import Error, transaction
from django.db.models import Q

from app.lib import helpers, loaders
from app.lib.nlp import summarizer
from app.lib.utils import parallel
from app.models import *


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

        (review, patchsets) = item

        cnt = 0
        with transaction.atomic():
            try:
                for (author, psid, ps) in patchsets:
                    patchset = PatchSet(
                            review=review, id=psid, created=ps['created']
                        )
                    patchset.save()

                    files = list()
                    for (path, p) in ps['files'].items():
                        patch = Patch(
                                patchset=patchset, id=p['id'], path=path,
                                num_added=p['num_added'],
                                num_removed=p['num_removed']
                            )
                        patch.save()

                        files.append(path)
                        if 'messages' in p:
                            previous = dict()
                            for i, m in enumerate(p['messages']):
                                line = m['lineno']
                                if line not in previous:
                                    previous[line] = list()
                                comment = Comment(
                                        patch=patch, posted=m['date'],
                                        line=line, author=m['author_email'],
                                        text=helpers.clean(m['text']),
                                        by_reviewer=m['author_email'] != author
                                    )
                                comment.parent = helpers.get_parent(
                                        m['text'], previous[line]
                                    )
                                comment.save()
                                previous[line].append(comment)
                                cnt += 1
                    if files:
                        patchset.files = files
                        patchset.save()
            except Error as err:  # pragma: no cover
                sys.stderr.write('Exception\n')
                sys.stderr.write('  Review  {}\n'.format(review.id))
                extype, exvalue, extrace = sys.exc_info()
                traceback.print_exception(extype, exvalue, extrace)

        cqueue.put(cnt)


def stream(review_ids, settings, iqueue, num_doers):
    for review_id in review_ids:
        review = helpers.get_row(Review, id=review_id)
        if review is not None:
            author = review.document['owner_email']

            patchsets = list()
            for (psid, ps) in review.document['patchsets'].items():
                patchsets.append((author, psid, ps))
            iqueue.put((review, patchsets))

    for i in range(num_doers):
        iqueue.put(parallel.EOI)


class CommentLoader(loaders.Loader):
    def __init__(self, settings, num_processes, review_ids):
        super(CommentLoader, self).__init__(settings, num_processes)
        self.review_ids = review_ids

    def load(self):
        iqueue = parallel.manager.Queue(self.settings.QUEUE_SIZE)

        process = self._start_streaming(iqueue)
        count = parallel.run(do, aggregate, iqueue, self.num_processes)
        process.join()

        return count

    def _start_streaming(self, iqueue):
        process = multiprocessing.Process(
                target=stream,
                args=(
                    self.review_ids, self.settings, iqueue, self.num_processes
                )
            )
        process.start()

        return process
