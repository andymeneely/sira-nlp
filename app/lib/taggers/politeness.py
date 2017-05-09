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


def aggregate(oqueue, cqueue, num_doers):
    count, done = 0, 0
    while True:
        item = cqueue.get()
        if item == parallel.DD:
            done += 1
            if done == num_doers:
                break
            continue # pragma: no cover

        count += item[0]
    oqueue.put(count)


def do(iqueue, cqueue): # pragma: no cover
    while True:
        item = iqueue.get()
        if item == parallel.EOI:
            cqueue.put(parallel.DD)
            break

        (sent) = item
        with transaction.atomic():
            try:
                results = analyzers.PolitenessAnalyzer(sent.text,
                                                       sent.parses['depparse'],
                                                  ).analyze()
                sent.metrics['politeness'] = results
                sent.save()
            except Error as err: # pragma: no cover
                sys.stderr.write('Exception\n')
                sys.stderr.write('  Sentence  {}\n'.format(sentence.id))
                extype, exvalue, extrace = sys.exc_info()
                traceback.print_exception(extype, exvalue, extrace)

        cqueue.put((1, sent.id))


def stream(sentenceObjects, iqueue, num_doers):
    for sentence in sentenceObjects:
        iqueue.put((sentence))

    for i in range(num_doers):
        iqueue.put(parallel.EOI)


class PolitenessTagger(taggers.Tagger):
    def __init__(self, settings, num_processes, sentenceObjects):
        super(PolitenessTagger, self).__init__(settings, num_processes)
        self.sentenceObjects = sentenceObjects

    def tag(self):
        iqueue = parallel.manager.Queue(self.settings.QUEUE_SIZE)

        process = self._start_streaming(iqueue)
        count = parallel.run(do, aggregate, iqueue, self.num_processes)
        process.join()

        return count

    def _start_streaming(self, iqueue):
        process = multiprocessing.Process(
                target=stream,
                args=(self.sentenceObjects, iqueue, self.num_processes)
            )
        process.start()

        return process
