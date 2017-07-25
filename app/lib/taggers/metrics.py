import _pickle
import multiprocessing
import re
import sys
import traceback

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from django.db import Error, transaction

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

        (sent, tokens, metrics) = item
        with transaction.atomic():
            try:
                if 'formality' in metrics:
                    results = analyzers.FormalityAnalyzer(sent.text, tokens).analyze()
                    sent.metrics['formality'] = "formal" if results == "F" else "informal"
                if 'informativeness' in metrics:
                    results = analyzers.InformativenessAnalyzer(sent.text, tokens).analyze()
                    sent.metrics['informativeness'] = "informative" if results == "I" else "uninformative"
                if 'implicature' in metrics:
                    results = analyzers.ImplicatureAnalyzer(sent.text, tokens).analyze()
                    sent.metrics['implicature'] = "implicative" if results == "I" else "unimplicative"

                sent.save()
            except Error as err: # pragma: no cover
                sys.stderr.write('Exception\n')
                sys.stderr.write('  Sentence  {}\n'.format(sent.id))
                extype, exvalue, extrace = sys.exc_info()
                traceback.print_exception(extype, exvalue, extrace)

        cqueue.put((1, sent.id))


def stream(sentenceObjects, iqueue, num_doers, metrics):
    for sentence in sentenceObjects:
        # TODO: Move query to queryStrings
        tokens = Token.objects.filter(sentence_id__exact=sentence.id).values()
        iqueue.put((sentence, tokens, metrics))

    for i in range(num_doers):
        iqueue.put(parallel.EOI)


class MetricsTagger(taggers.Tagger):
    def __init__(self, settings, num_processes, sentenceObjects, metrics):
        super(MetricsTagger, self).__init__(settings, num_processes)
        self.sentenceObjects = sentenceObjects
        self.metrics = metrics

    def tag(self):
        iqueue = parallel.manager.Queue(self.settings.QUEUE_SIZE)

        process = self._start_streaming(iqueue)
        count = parallel.run(do, aggregate, iqueue, self.num_processes)
        process.join()

        return count

    def _start_streaming(self, iqueue):
        process = multiprocessing.Process(
                target=stream,
                args=(
                    self.sentenceObjects, iqueue, self.num_processes,
                    self.metrics
                )
            )
        process.start()

        return process
