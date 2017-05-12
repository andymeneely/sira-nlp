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

def get_sent_label(tokens):

def aggregate(oqueue, cqueue, num_doers):
    count, done = 0, 0
    while True:
        item = cqueue.get()
        if item == parallel.DD:
            done += 1
            if done == num_doers:
                break
            continue # pragma: no cover

        count += 1
    oqueue.put(count)


def do(iqueue, cqueue): # pragma: no cover
    while True:
        item = iqueue.get()
        if item == parallel.EOI:
            cqueue.put(parallel.DD)
            break

        (sent, tokens, root) = item
        with transaction.atomic():
            try:
                results = analyzers.UncertaintyAnalyzer(tokens, root).analyze()

                u_results = {k:v for k, v in results.items() if v != 'C'}
                if bool(u_results): # if there are entries in u_results
                    sent_label = get_sent_label(list(u_results.values())
                    sent.metrics['uncertainty'] = sent_label
                    sent.save()
                    for k, v in u_results.items():
                        # token.uncertainty = v
                        # token.save()

            except Error as err: # pragma: no cover
                sys.stderr.write('Exception\n')
                sys.stderr.write('  Sentence  {}\n'.format(sent.id))
                extype, exvalue, extrace = sys.exc_info()
                traceback.print_exception(extype, exvalue, extrace)

        cqueue.put(1)


def stream(sentenceObjects, iqueue, num_doers, root):
    for sentence in sentenceObjects:
        tokens = Token.objects.filter(sentence_id__exact=sentence.id)
        iqueue.put((sentence, tokens, root))

    for i in range(num_doers):
        iqueue.put(parallel.EOI)


class UncertaintyTagger(taggers.Tagger):
    def __init__(self, settings, num_processes, sentenceObjects, root_type):
        super(UncertaintyTagger, self).__init__(settings, num_processes)
        self.sentenceObjects = sentenceObjects
        self.root = root_type

    def tag(self):
        iqueue = parallel.manager.Queue(self.settings.QUEUE_SIZE)

        process = self._start_streaming(iqueue)
        count = parallel.run(do, aggregate, iqueue, self.num_processes)
        process.join()

        return count

    def _start_streaming(self, iqueue):
        process = multiprocessing.Process(
                target=stream,
                args=(self.sentenceObjects, iqueue, self.num_processes, self.root)
            )
        process.start()

        return process
