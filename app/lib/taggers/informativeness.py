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

from app.lib.external import (INFORMATIVENESS_CLASSIFIER_PATH,
                              INFORMATIVENESS_VECTORIZER_PATH)
from app.lib.external.squinky_corpus.word import _Word

with open(INFORMATIVENESS_CLASSIFIER_PATH, 'rb') as f:
    CLS = _pickle.load(f)
with open(INFORMATIVENESS_VECTORIZER_PATH, 'rb') as f:
    VEC = _pickle.load(f)


def _score(sent, tokens): # pragma: no cover
    words = list()
    for i, tok in enumerate(list(tokens)):
        prev = tokens[i-1]['token'] if i-1 >= 0 else None
        next = tokens[i+1]['token'] if i+1 < len(tokens) else None
        w = _Word(tok['token'], tok['pos'], tok['position'], prev, next,
                  tok['chunk'])
        words.append(w)

    feats = dict()
    for word in words:
        feats.update(word.get_features())
    fv = VEC.transform(feats)
    probs = CLS.predict_proba(fv)

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

        (sent, tokens) = item
        with transaction.atomic():
            try:
                results = _score(sent, tokens)
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
        tokens = Token.objects.filter(sentence_id__exact=sentence.id).values()
        iqueue.put((sentence, tokens))

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
