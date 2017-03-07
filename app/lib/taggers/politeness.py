import multiprocessing
import sys
import traceback

from django.db import Error, transaction
from django.db.models import Q

from app.lib import taggers
from app.lib.nlp import analyzers
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
            continue
        count += item
    oqueue.put(count)


def do(iqueue, cqueue):
    while True:
        item = iqueue.get()
        if item == parallel.EOI:
            cqueue.put(parallel.DD)
            break

        (review_id, messages) = item
        count = 0
        with transaction.atomic():
            try:
                for message in messages:
                    parses = list(message.parse)
                    sents = list()
                    for p in parses:
                        temp = list()
                        for t in p:
                            x = re.sub(r'\s+', ' ', re.sub(r'\(\[^\s\]*', '', t))
                            temp.append(x)
                        sents.append(temp)

                    # FIXME: SentimentAnalyzer is using the default value for
                    # its url (http://localhost:9000). Use a settings constant
                    # instead.
                    message.politeness = (
                            analyzers.PolitenessAnalyzer(message.text, parses, sents).analyze()
                        )
                    message.save()
                    count += 1
            except Error as err:
                sys.stderr.write('Exception\n')
                sys.stderr.write('  Review  {}\n'.format(review_id))
                extype, exvalue, extrace = sys.exc_info()
                traceback.print_exception(extype, exvalue, extrace)

        cqueue.put(count)


def stream(review_ids, iqueue, num_doers):
    for review_id in review_ids:
        messages = list(
                Message.objects.filter(review_id=review_id).exclude(text='')
            )
        iqueue.put((review_id, messages))

    for i in range(num_doers):
        iqueue.put(parallel.EOI)


class PolitenessTagger(taggers.Tagger):
    def __init__(self, settings, num_processes, review_ids):
        super(PolitenessTagger, self).__init__(settings, num_processes)
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
