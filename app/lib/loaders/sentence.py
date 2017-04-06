import multiprocessing
import sys
import traceback

from django.db import Error, transaction

from app.lib import helpers, loaders
from app.lib.nlp import summarizer, sentenizer
from app.lib.utils import parallel
from app.models import *
from app.queryStrings import *


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

        (review_id, messages) = item

        objects = list()
        with transaction.atomic():
            try:
                for (posted, sender, text, message_id) in messages:
                    for sent in sentenizer.NLTKSentenizer(text).execute():
                        objects.append(Sentence(
                                review_id=review_id,
                                message_id=message_id,
                                text=sent
                            ))
                if len(objects) > 0:
                    Sentence.objects.bulk_create(objects)
            except Error as err: # pragma: no cover
                sys.stderr.write('Exception\n')
                sys.stderr.write('  Review  {}\n'.format(review_id))
                extype, exvalue, extrace = sys.exc_info()
                traceback.print_exception(extype, exvalue, extrace)

        cqueue.put(len(objects))


def stream(review_ids, settings, iqueue, num_doers):
    for review_id in review_ids:
        review = helpers.get_row(Review, id=review_id)

        messages = []
        for message in Message.objects.filter(review_id__exact=review_id):
            if message.sender in settings.BOTS:
                continue # pragma: no cover
            messages.append((message.posted, message.sender, message.text, message.id))
        iqueue.put((review_id, messages))

    for i in range(num_doers):
        iqueue.put(parallel.EOI)


class SentenceLoader(loaders.Loader):
    def __init__(self, settings, num_processes, review_ids):
        super(SentenceLoader, self).__init__(settings, num_processes)
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
