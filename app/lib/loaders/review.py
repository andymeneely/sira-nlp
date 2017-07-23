"""
@AUTHOR: nuthanmunaiah
"""

import multiprocessing
import sys
import traceback

from django.db import connection, Error, transaction

from app.lib import files, helpers, loaders
from app.lib.utils import parallel
from app.models import *


def aggregate(oqueue, cqueue, num_doers):
    count, done = 0, 0
    while True:
        item = cqueue.get()
        if item == parallel.DD:
            done += 1
            if done == num_doers:
                break   # All doers are done
            continue  # pragma: no cover

        (review, bug_ids) = item
        try:
            with transaction.atomic():
                review.save()

                review_bugs = list()
                for id in bug_ids:
                    bug = helpers.get_row(Bug, id=id)
                    if bug is not None:
                        review_bugs.append(ReviewBug(review=review, bug=bug))
                if review_bugs:
                    ReviewBug.objects.bulk_create(review_bugs)
                count += 1
        except Error as err:  # pragma: no cover
            sys.stderr.write('Exception\n')
            sys.stderr.write('  Review  {}\n'.format(review.id))
            extype, exvalue, extrace = sys.exc_info()
            traceback.print_exception(extype, exvalue, extrace)

    oqueue.put(count)


def do(iqueue, cqueue):  # pragma: no cover
    while True:
        item = iqueue.get()
        if item == parallel.EOI:
            cqueue.put(parallel.DD)
            break

        review = Review(
                id=item['issue'], created=item['created'],
                is_open=True if not item['closed'] else False,
                num_messages=len(item['messages']), document=item
            )
        bug_ids = set(helpers.parse_bugids(item['description']))

        cqueue.put((review, bug_ids))


def stream(iqueue, settings, num_doers):
    f = files.Files(settings)
    for year in settings.YEARS:
        for review in f.get_reviews(year):
            iqueue.put(f.transform_review(review))

    for i in range(num_doers):
        iqueue.put(parallel.EOI)


class ReviewLoader(loaders.Loader):
    """
    Implements loader object.
    """
    def load(self):
        """
        Grabs all of the reviews created within the specified range of years,
        parses them, cleans them up, and saves them. Returns the total number
        of loaded reviews.
        """
        count = 0

        iqueue = parallel.manager.Queue(self.settings.QUEUE_SIZE)
        process = self._start_streaming(iqueue)
        count = parallel.run(do, aggregate, iqueue, self.num_processes)
        process.join()

        self._cluster()

        return count

    def _cluster(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute('CLUSTER review USING review_created_idx')
        except Error as err:
            sys.stderr.write('Exception\n')
            extype, exvalue, extrace = sys.exc_info()
            traceback.print_exception(extype, exvalue, extrace)

    def _start_streaming(self, iqueue):
        process = multiprocessing.Process(
                target=stream, args=(iqueue, self.settings, self.num_processes)
            )
        process.start()
        return process
