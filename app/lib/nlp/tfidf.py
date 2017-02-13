"""
@AUTHOR: nuthanmunaiah
@AUTHOR: meyersbs
"""

import multiprocessing
import sys
import traceback

from django.db.models import Sum

from app.lib.utils import parallel
from app.models import *
from app.queryStrings import *

IDF = None
USE_LEMMA = False

def aggregate(oqueue, cqueue, num_doers):
    done = 0
    tfidfs = dict()
    while True:
        item = cqueue.get()
        if item == parallel.DD:
            done += 1
            if done == num_doers:
                break
            continue
        (review_id, tfidf) = item
        tfidfs[review_id] = tfidf
    oqueue.put(tfidfs)


def do(iqueue, cqueue):
    global USE_LEMMA
    while True:
        item = iqueue.get()
        if item == parallel.EOI:
            cqueue.put(parallel.DD)
            break

        review_id = item

        try:
            # Dictionary of { 'token': frequency }.
            # The numerator of TF for every token in the review.
            tfs = query_TF_dict(review_id, USE_LEMMA)

            # The total number of tokens in the review.
            num_tokens = tfs.aggregate(nt=Sum('frequency'))['nt']

            # Compute the TF-IDF for every token in the review against the
            # entire corpus of reviews.
            tfidf = dict()
            if num_tokens is not None:
                if USE_LEMMA:
                    for entry in tfs:
                        (lemma, tf) = (entry['lemma'], entry['tf'])
                        tfidf[lemma] = tf / float(num_tokens) * IDF.get(lemma, 0)
                else:
                    for entry in tfs:
                        (token, tf) = (entry['token'], entry['tf'])
                        tfidf[token] = tf / float(num_tokens) * IDF.get(token, 0)

            cqueue.put((review_id, tfidf))
        except Exception as e:
            sys.stderr.write('Exception\n')
            sys.stderr.write('\tReview {}\n'.format(review_id))
            e_type, e_value, e_trace = sys.exc_info()
            traceback.print_exception(e_type, e_value, e_trace)

def stream(review_ids, iqueue, num_doers):
    for r in review_ids:
        iqueue.put(r)

    for i in range(num_doers):
        iqueue.put(parallel.EOI)

def compute(review_ids, idf, num_procs, use_lemma=False):
    if idf is None or type(idf) is not dict:
        raise ValueError('Argument IDF must be a dictionary!')

    global IDF, USE_LEMMA
    IDF = idf
    USE_LEMMA = use_lemma

    iqueue = parallel.manager.Queue()
    proc = multiprocessing.Process(
            target=stream, args=(review_ids, iqueue, num_procs)
        )
    proc.start()
    tfidfs = parallel.run(do, aggregate, iqueue, num_procs)
    proc.join()

    return tfidfs
