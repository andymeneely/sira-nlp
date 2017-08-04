import multiprocessing
import sys
import traceback

from django.db import Error, transaction

from splat.complexity import *

from app.lib import taggers, logger, helpers
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
            continue  # pragma: no cover

        count += item[0]
    oqueue.put(count)


def do(iqueue, cqueue):  # pragma: no cover
    while True:
        item = iqueue.get()
        if item == parallel.EOI:
            cqueue.put(parallel.DD)
            break

        (sent, metrics) = item
        with transaction.atomic():
            try:
                tokens = sent.token_set.all().values_list('token', 'pos')

                if metrics and 'baselines' not in sent.metrics:
                    sent.metrics['baselines'] = dict()

                if 'sent_length' in metrics:
                    sent.metrics['baselines']['length'] = tokens.count()
                if 'type_token_ratio' in metrics:
                    results = helpers.get_type_token_ratio(tokens)
                    sent.metrics['baselines']['type_token_ratio'] = results
                if 'pronoun_density' in metrics:
                    results = helpers.get_pronoun_density(tokens)
                    sent.metrics['baselines']['pronoun_density'] = results
                if 'flesch_kincaid' in metrics:
                    toks = [t[0] for t in tokens]
                    results = calc_flesch_kincaid(
                            # wordcount, sentcount, syllcount
                            len(toks), 1, helpers.get_syllable_count(toks)
                        )
                    sent.metrics['baselines']['flesch_kincaid'] = results
                if 'stop_word_ratio' in metrics:
                    logger.warning("NotImplemented: 'stop_word_ratio'")
                if 'question_ratio' in metrics:
                    logger.warning("NotImplemented: 'question_ratio'")
                if 'conceptual_similarity' in metrics:
                    logger.warning("NotImplemented: 'conceptual_similarity'")

                sent.save()
            except Error as err:  # pragma: no cover
                sys.stderr.write('Exception\n')
                sys.stderr.write('  Sentence  {}\n'.format(sent.id))
                extype, exvalue, extrace = sys.exc_info()
                traceback.print_exception(extype, exvalue, extrace)

        cqueue.put((1, sent.id))


def stream(sentenceObjects, iqueue, num_doers, metrics):
    for sentence in sentenceObjects:
        iqueue.put((sentence, metrics))

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
