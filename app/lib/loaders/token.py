import multiprocessing
import sys
import traceback

from django.db import Error, transaction
from django.db.models import Q
from app.lib import helpers, loaders
from app.lib.nlp import summarizer
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
        count += item
    oqueue.put(count)


def do(iqueue, cqueue):  # pragma: no cover
    while True:
        item = iqueue.get()
        if item == parallel.EOI:
            cqueue.put(parallel.DD)
            break

        (review_id, sentences) = item

        objects = list()
        with transaction.atomic():
            try:
                for (sentence_id, sentence_text) in sentences:
                    summary = summarizer.Summarizer(sentence_text).execute()
                    for (position, token, stem, lemma, pos, chunk) in summary:
                        objects.append(Token(
                                sentence_id=sentence_id, position=position,
                                token=token, stem=stem, lemma=lemma, pos=pos,
                                chunk=chunk
                            ))

                if len(objects) > 0:
                    Token.objects.bulk_create(objects)
            except Error as err:  # pragma: no cover
                sys.stderr.write('Exception\n')
                sys.stderr.write('  Review  {}\n'.format(review_id))
                extype, exvalue, extrace = sys.exc_info()
                traceback.print_exception(extype, exvalue, extrace)

        cqueue.put(len(objects))


def stream(review_ids, settings, iqueue, num_doers):
    for review_id in review_ids:
        sentences = list()
        q1 = Q(message__review_id=review_id)
        q2 = Q(comment__patch__patchset__review_id=review_id)
        #for sentence in Sentence.objects.filter(message__review_id=review_id):
        for sentence in Sentence.objects.filter(q1 | q2):
            sentences.append((sentence.id, sentence.text))
        iqueue.put((review_id, sentences))

    for i in range(num_doers):
        iqueue.put(parallel.EOI)


class TokenLoader(loaders.Loader):
    def __init__(self, settings, num_processes, review_ids):
        super(TokenLoader, self).__init__(settings, num_processes)
        self.review_ids = review_ids

    def load(self):
        iqueue = parallel.manager.Queue(self.settings.QUEUE_SIZE)

        process = self._start_streaming(iqueue)
        count = parallel.run(do, aggregate, iqueue, self.num_processes)
        process.join()

        return count

    def _start_streaming(self, iqueue):
        process = multiprocessing.Process(
                target=stream,
                args=(
                    self.review_ids, self.settings, iqueue, self.num_processes
                )
            )
        process.start()

        return process
