import multiprocessing
import sys
import traceback

from django.db import Error, transaction
from django.db.models import Q

from app.lib import taggers
from app.lib.nlp import analyzers, sentenizer
from app.lib.utils import parallel
from app.models import *

ZEROS = False

def aggregate(oqueue, cqueue, num_doers):
    count, done = 0, 0
    while True:
        item = cqueue.get()
        if item == parallel.DD:
            done += 1
            if done == num_doers:
                break
            continue
        count += item
    oqueue.put(count)


def do(iqueue, cqueue):
    global ZEROS
    while True:
        item = iqueue.get()
        if item == parallel.EOI:
            cqueue.put(parallel.DD)
            break

        (review_id, messages, zeros) = item
        count = 0
        with transaction.atomic():
            try:
                if zeros:
                    for m in messages:
#                        print(m.parse)
                        if m.parse == []:
#                            print(m.parse)
                            results = analyzers.ComplexityAnalyzer(m.text).analyze()
                            m.complexity = (results[0])
                            m.parse = (results[1])
                            print(str(m.id) + ":\t" + str(m.complexity))
                            m.save()
                        else:
                            pass
#                            print("Skipped " + str(m.id) + ":\t" + str(m.complexity))
                else:
                    for m in messages:
                        results = analyzers.ComplexityAnalyzer(m.text).analyze()
#                        print(str(m.id) + ":\t" + str(results[0]) + "\n" + str(results[1]))
                        m.complexity = (results[0])
                        m.parse = (results[1])
                        print(str(m.id) + ":\t" + str(m.complexity))
#                        print(str(m.id) + ":\t" + str(m.parse))
                        m.save()
                count += 1
            except Error as err:
                sys.stderr.write('Exception\n')
                sys.stderr.write('  Review  {}\n'.format(review_id))
                extype, exvalue, extrace = sys.exc_info()
                traceback.print_exception(extype, exvalue, extrace)

        cqueue.put(count)


def stream(review_ids, iqueue, num_doers, zeros):
    for review_id in review_ids:
        messages = list(
                Message.objects.filter(review_id=review_id).exclude(text='')
            )
        iqueue.put((review_id, messages, zeros))

    for i in range(num_doers):
        iqueue.put(parallel.EOI)


class ComplexityTagger(taggers.Tagger):
    def __init__(self, settings, num_processes, review_ids, zeros):
        super(ComplexityTagger, self).__init__(settings, num_processes)
        self.review_ids = review_ids
        self.zeros = zeros

    def tag(self):
        iqueue = parallel.manager.Queue(self.settings.QUEUE_SIZE)

        process = self._start_streaming(iqueue)
        count = parallel.run(do, aggregate, iqueue, self.num_processes)
        process.join()

        return count

    def _start_streaming(self, iqueue):
        process = multiprocessing.Process(
                target=stream,
                args=(self.review_ids, iqueue, self.num_processes, self.zeros)
            )
#        print(self.review_ids)
        process.start()

        return process
