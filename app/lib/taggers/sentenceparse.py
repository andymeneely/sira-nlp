"""
@AUTHOR: meyersbs
"""

import multiprocessing
import json
import re
import sys
import time
import traceback

from datetime import datetime as dt

from django.db import Error, transaction
from django.db.models import Q

from app.lib import taggers, logger, helpers
from app.lib.nlp import analyzers, sentenizer
from app.lib.utils import parallel
from app.models import *

from bulk_update.helper import bulk_update

def clean_depparse(dep):
    """
    Given a dependency dictionary, return a formatted string representation.
    """
    return str(dep['dep'] + "(" + dep['governorGloss'].lower() + "-" +
               str(dep['governor']) + ", " + dep['dependentGloss'] + "-" +
               str(dep['dependent']) + ")")

def clean_treeparse(tree):
    """
    Given a string representation of a syntactic tree, remove duplicate
    spaces, all newlines, and the initial 'ROOT' tag that the Stanford
    CoreNLP includes in the parse string.
    """
    try:
        cleaned_tree = re.sub(r' {2,}', ' ', tree)
        cleaned_tree = re.sub(r'\n', '', cleaned_tree)
        cleaned_tree = re.sub(r'ROOT', '', cleaned_tree)
        return cleaned_tree
    except TypeError as e:
        # BEN: I saw one regex fail because the given tree was '[]'
        logger.error("REGEX FAILED: " + str(tree))
        return "RegexFailed"

def aggregate(oqueue, cqueue, num_doers):
    count, done, cnt, threshhold = 0, 0, 0, 1000
    sentences = []
    while True:
        item = cqueue.get()
        if item == parallel.DD:
            done += 1
            if done == num_doers:
                break
            continue
        else:
            sentences.append(item[0])
            sent_len = len(sentences)
            if sent_len > threshhold:
                start = dt.now()
                bulk_update(sentences[sent_len-threshhold:],
                            update_fields=['parses'])
                logger.info("Saved " + str(threshhold) +
                            " rows in {:.2f} minutes."
                            .format(helpers.get_elapsed(start, dt.now())))
                sentences = []
#            logger.warning("CQUEUE SIZE: " + str(cqueue.qsize()))
            continue
        count += item
    oqueue.put(count)

def do(iqueue, cqueue):
    while True:
        item = iqueue.get()
        if item == parallel.EOI:
            cqueue.put(parallel.DD)
            break

        (sentence) = item
        count = 0
        result = {}
        with transaction.atomic():
            try:
                # Hand the sentence text off to the analyzer
                resp = analyzers.SentenceParseAnalyzer(sentence.text).analyze()
#                time.sleep(1)
                parse, depparse = [], []
                # If the SentenceParseAnalyzer failed to parse the sentence
                if resp['deps'] == 'X' or resp['trees'] == 'X':
                    result['depparse'], result['treeparse'] = 'X', 'X'
                else:
                    for dep in resp['deps']:
                        depparse.append(clean_depparse(dep))
                    result['depparse'] = depparse
                    result['treeparse'] = clean_treeparse(resp['trees'])

                sentence.parses = result
#                logger.info("PROCESSED: " + str(sentence.id))
                count += 1
            except Error as err:
                sys.stderr.write('Exception\n')
                sys.stderr.write('  Sentence  {}\n'.format(sentence.id))
                extype, exvalue, extrace = sys.exc_info()
                traceback.print_exception(extype, exvalue, extrace)

        # Give the aggregate() function some time to handle the cqueue.
        if cqueue.qsize() > 1000:
            time.sleep(10)
        cqueue.put((sentence, count))

def stream(sentences, iqueue, num_doers):
    for sentence in sentences:
        iqueue.put((sentence))

    for i in range(num_doers):
        iqueue.put(parallel.EOI)


class SentenceParseTagger(taggers.Tagger):
    def __init__(self, settings, num_processes, sentences):
        super(SentenceParseTagger, self).__init__(settings, num_processes)
        self.sentences = sentences

    def tag(self):
        iqueue = parallel.manager.Queue(self.settings.QUEUE_SIZE)

        process = self._start_streaming(iqueue)
        count = parallel.run(do, aggregate, iqueue, self.num_processes)
        process.join()

        return count

    def _start_streaming(self, iqueue):
        process = multiprocessing.Process(
                target=stream,
                args=(self.sentences, iqueue, self.num_processes)
            )
        process.start()

        return process
