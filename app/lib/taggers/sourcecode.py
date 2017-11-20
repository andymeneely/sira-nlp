import multiprocessing
import re
import sys
import traceback

from django.db import Error, transaction
from django.db.models import Q

from app.lib import taggers, logger
from app.lib.nlp import analyzers, sentenizer
from app.lib.utils import parallel
from app.models import *


CAMELCASE_RE = re.compile('([A-Z][a-z0-9]+){2,}')
CODECHARS_RE = re.compile('[<>\{\}\[\]\\~`_\=\+\^]')


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

        (tok) = item
        cnt = 0
        with transaction.atomic():
            try:
                if (CODECHARS_RE.search(tok.token) is not None or
                    CAMELCASE_RE.search(tok.token) is not None):
                    print("CODE: " + str(tok.token))
                    tok.is_code = True
                    tok.save()
                    cnt += 1

            except Error as err: # pragma: no cover
                sys.stderr.write('Exception\n')
                sys.stderr.write('  Token:  {}\n'.format(tok.id))
                extype, exvalue, extrace = sys.exc_info()
                traceback.print_exception(extype, exvalue, extrace)

        cqueue.put(cnt)


def stream(tokens, iqueue, num_doers):
    print(tokens)
    for token in tokens:
        iqueue.put((token))

    for i in range(num_doers):
        iqueue.put(parallel.EOI)


class SourceCodeTagger(taggers.Tagger):
    def __init__(self, settings, num_processes, tokenObjects):
        super(SourceCodeTagger, self).__init__(settings, num_processes)
        self.tokenObjects = tokenObjects

    def tag(self):
        iqueue = parallel.manager.Queue(self.settings.QUEUE_SIZE)

        process = self._start_streaming(iqueue)
        count = parallel.run(do, aggregate, iqueue, self.num_processes)
        process.join()

        return count

    def _start_streaming(self, iqueue):
        process = multiprocessing.Process(
                target=stream,
                args=(self.tokenObjects, iqueue, self.num_processes)
            )
        process.start()

        return process
