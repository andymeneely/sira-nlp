import multiprocessing
import sys
import traceback

from django.db import Error, transaction
from django.db.models import Q

from app.lib import taggers, logger
from app.lib.nlp import analyzers, sentenizer
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
        count += item
    oqueue.put(count)


def do(iqueue, cqueue): # pragma: no cover
    while True:
        item = iqueue.get()
        if item == parallel.EOI:
            cqueue.put(parallel.DD)
            break

        (sent) = item
        count = 0
        with transaction.atomic():
            try:
                new_form = {'formal': None, 'informal': None}
                new_info = {'informative': None, 'uninformative': None}
                new_impl = {'implicative': None, 'unimplicative': None}

                new_form['formal'] = sent.metrics['formality']['informal']
                new_form['informal'] = sent.metrics['formality']['formal']

                new_info['informative'] = sent.metrics['informativeness']['uninformative']
                new_info['uninformative'] = sent.metrics['informativeness']['informative']

                new_impl['implicative'] = sent.metrics['implicature']['unimplicative']
                new_impl['unimplicative'] = sent.metrics['implicature']['implicative']

                sent.metrics['formality'] = new_form
                sent.metrics['informativeness'] = new_info
                sent.metrics['implicature'] = new_impl
                sent.save()

                count += 1
            except Error as err: # pragma: no cover
                sys.stderr.write('Exception\n')
                sys.stderr.write('  Sentence:  {}\n'.format(sent.id))
                extype, exvalue, extrace = sys.exc_info()
                traceback.print_exception(extype, exvalue, extrace)

        cqueue.put(count)


def stream(sentences, iqueue, num_doers):
    for sentence in sentences:
        iqueue.put((sentence))

    for i in range(num_doers):
        iqueue.put(parallel.EOI)


class FixSquinkyTagger(taggers.Tagger):
    def __init__(self, settings, num_processes, sentObjects):
        super(FixSquinkyTagger, self).__init__(settings, num_processes)
        self.sentObjects = sentObjects

    def tag(self):
        iqueue = parallel.manager.Queue(self.settings.QUEUE_SIZE)

        process = self._start_streaming(iqueue)
        count = parallel.run(do, aggregate, iqueue, self.num_processes)
        process.join()

        return count

    def _start_streaming(self, iqueue):
        process = multiprocessing.Process(
                target=stream,
                args=(self.sentObjects, iqueue, self.num_processes)
            )
        process.start()

        return process
