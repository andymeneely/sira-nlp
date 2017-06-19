import _pickle
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

from app.lib.external import (INFORMATIVENESS_CLASSIFIER_PATH,
                              INFORMATIVENESS_VECTORIZER_PATH)

CLS = _pickle.load(INFORMATIVENESS_CLASSIFIER_PATH)
VEC = _pickle.load(INFORMATIVENESS_VECTORIZER_PATH)

def _score(sent):
    # Vectorizer returns {feature-name: value} dict
    features = VEC.features(request)
    fv = [features[f] for f in sorted(features.keys())]
    # Single-row sparse matrix
    X = csr_matrix(np.asarray([fv]))
    probs = CLS.predict_proba(X)

    return {"informative": probs[0][1], "uninformative": probs[0][0]}


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
                results = _score(sent.text)
                sent.metrics['informativeness'] = results
                sent.save()
            except Error as err: # pragma: no cover
                sys.stderr.write('Exception\n')
                sys.stderr.write('  Sentence  {}\n'.format(sent.id))
                extype, exvalue, extrace = sys.exc_info()
                traceback.print_exception(extype, exvalue, extrace)

        cqueue.put((1, sent.id))


def stream(sentenceObjects, iqueue, num_doers):
    for sentence in sentenceObjects:
        iqueue.put((sentence))

    for i in range(num_doers):
        iqueue.put(parallel.EOI)


class InformativenessTagger(taggers.Tagger):
    def __init__(self, settings, num_processes, sentenceObjects):
        super(InformativenessTagger, self).__init__(settings, num_processes)
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
