import multiprocessing
import re
import sys
import traceback

from django.db import Error, transaction
from django.db.models import Q

from splat.complexity import open_class_list, closed_class_list

from app.lib import taggers, logger
from app.lib.nlp import analyzers, sentenizer
from app.lib.utils import parallel
from app.models import *


def __calc_content_density(tags):
    open_count, closed_count = 0, 0
    for tag in tags:
        if tag in open_class_list:
            open_count += 1
        elif tag in closed_class_list:
            closed_count += 1
        else:
            logger.warning("Unknown tag " + tag + "\n")

    return float(open_count / closed_count) if closed_count != 0 else 0


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

        (comm) = item
        count = 0
        with transaction.atomic():
            try:
                tags = list()
                for sent in comm.sentences.iterator():
                    if sent.parses['treeparse'] != 'null':
                        tags += re.findall("\((\S+) [^\(^\)]*\)", sent.parses['treeparse'])

                c_density = __calc_content_density(tags)
                comm.metrics['complexity'] = dict()

                comm.metrics['complexity']['cdensity'] = c_density
                comm.save()

                count += 1
            except Error as err: # pragma: no cover
                sys.stderr.write('Exception\n')
                sys.stderr.write('  Sentence:  {}\n'.format(sent.id))
                extype, exvalue, extrace = sys.exc_info()
                traceback.print_exception(extype, exvalue, extrace)

        cqueue.put(count)


def stream(comments, iqueue, num_doers):
    for comment in comments:
        #sents = comment.sentences #Sentence.objects.filter(comment_sentences__comment_id=comment.id).iterator()
        iqueue.put((comment))

    for i in range(num_doers):
        iqueue.put(parallel.EOI)


class CommentLevelTagger(taggers.Tagger):
    def __init__(self, settings, num_processes, commObjects):
        super(CommentLevelTagger, self).__init__(settings, num_processes)
        self.commObjects = commObjects

    def tag(self):
        iqueue = parallel.manager.Queue(self.settings.QUEUE_SIZE)

        process = self._start_streaming(iqueue)
        count = parallel.run(do, aggregate, iqueue, self.num_processes)
        process.join()

        return count

    def _start_streaming(self, iqueue):
        process = multiprocessing.Process(
                target=stream,
                args=(self.commObjects, iqueue, self.num_processes)
            )
        process.start()

        return process
