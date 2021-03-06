"""
@AUTHOR: meyersbs
"""

import multiprocessing
import json
import re
import sys
import time
import traceback

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from datetime import datetime as dt

from django.db import Error, transaction
from django.db.models import Q

from app.lib import taggers, logger, helpers
from app.lib.nlp import analyzers, sentenizer
from app.lib.utils import parallel
from app.models import *



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
        logger.error("REGEX FAILED: " + str(tree))
        return "RegexFailed"

def aggregate(oqueue, cqueue, num_doers):
    count, done = 0, 0
    sentences = []
    while True:
        item = cqueue.get()
        if item == parallel.DD:
            done += 1
            if done == num_doers:
                break
            continue # pragma: no cover

        Sentence.objects.filter(id=item[1]).update(parses=item[2])
        count += item[0]
    oqueue.put(count)

def do(iqueue, cqueue): # pragma: no cover
    while True:
        item = iqueue.get()
        if item == parallel.EOI:
            cqueue.put(parallel.DD)
            break

        (sent_id, sent_text, url) = item
        result = {}
        with transaction.atomic():
            try:
                # Hand the sentence text off to the analyzer
                resp = analyzers.SentenceParseAnalyzer(sent_text, url).analyze()
                parse, depparse = [], []
                # If the SentenceParseAnalyzer failed to parse the sentence
                if resp['deps'] == helpers.JSON_NULL \
                    or resp['trees'] == helpers.JSON_NULL:
                    result['depparse'] = helpers.JSON_NULL
                    result['treeparse'] = helpers.JSON_NULL
                else:
                    for dep in resp['deps']:
                        depparse.append(clean_depparse(dep))
                    result['depparse'] = depparse
                    result['treeparse'] = clean_treeparse(resp['trees'])

            except Error as err: # pragma: no cover
                sys.stderr.write('Exception\n')
                sys.stderr.write('  Sentence  {}\n'.format(sent_id))
                extype, exvalue, extrace = sys.exc_info()
                traceback.print_exception(extype, exvalue, extrace)

        cqueue.put((1, sent_id, result))

def stream(sentences, iqueue, num_doers):
    c = 0
    urls = [#"http://cluster-node-04.main.ad.rit.edu:41194/",
            #"http://cluster-node-02.main.ad.rit.edu:41194/",
            #"http://cluster-node-03.main.ad.rit.edu:41194/",
            "http://localhost:41194/"]
    for sentence in sentences:
        iqueue.put((sentence.id, sentence.text, urls[c]))
        if c < len(urls)-1: # pragma: no cover
            c += 1
        else:
           c = 0

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
