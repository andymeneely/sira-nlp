import _pickle
import multiprocessing
import re
import sys
import traceback

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from django.db import Error, transaction

from splat.complexity import *
from splat.corpora import *

from app.lib import taggers, logger, helpers
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
                if 'sent_length' in metrics:
                    results = len(tokens)
                    sent.metrics['length'] = results
                if 'type_token_ratio' in metrics:
                    results = helpers.get_type_token_ratio(tokens)
                    sent.metrics['type_token_ratio'] = results
                if 'pronoun_density' in metrics:
                    results = helpers.get_pronoun_density(tokens)
                    sent.metrics['pronoun_density'] = results
                if 'flesch_kincaid' in metrics:
                    toks = [ t[0] for t in tokens ]
                    results = calc_flesch_kincaid(
                            # wordcount, sentcount, syllcount
                            len(toks), 1, helpers.get_syllable_count(toks)
                        )
                    sent.metrics['flesch_kincaid'] = results
                if 'stop_word_ratio' in metrics:
                    logger.warning("NotImplemented: 'stop_word_ratio'")
                if 'question_ratio' in metrics:
                    logger.warning("NotImplemented: 'question_ratio'")
                if 'conceptual_similarity' in metrics:
                    logger.warning("NotImplemented: 'conceptual_similarity'")

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
        tokens = Token.objects.filter(sentence_id__exact=sentence.id) \
                      .values_list('token', 'pos')
        iqueue.put((sentence, tokens, metrics))

    for i in range(num_doers):
        iqueue.put(parallel.EOI)


class BaselinesTagger(taggers.Tagger):
    def __init__(self, settings, num_processes, sentenceObjects, metrics):
        super(BaselinesTagger, self).__init__(settings, num_processes)
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
