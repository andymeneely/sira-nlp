"""
@AUTHOR: meyersbs
"""

import math
import csv
import gc
import operator
import random
import itertools
import traceback
import re

from collections import OrderedDict
from datetime import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.db.models import Count, lookups, Lookup
from django.db.models.fields import Field

from app import TFIDF_TOKENS_PATH, TFIDF_LEMMAS_PATH
from app.lib import helpers, logger
from app.lib.nlp import tfidf
from app.models import *
from app.queryStrings import *

TF_IDFS = None
DECIMAL_PLACES = 100

def merge_dicts(dict_list):
    """
    Given a list of dictionaries, merge them all, appending values for
    duplicate keys to a list. Return a dictionary containing all unique keys
    and their maximum value.
    """
    d = {}
    for dic in dict_list:
        for key in dic.keys():
            try:
                d[key].append(dic[key])
            except KeyError:
                d[key] = [dic[key]]

    top_kv = {}
    for k, v in d.items():
        top_kv[k] = max(v)

    return top_kv

def to_csv(review_ids, tf_idfs, use_lemma, top=100):
    """ Convert the given TF-IDF dictionary to a CSV and write to disk. """
    global DECIMAL_PLACES
    logger.info('Saving TF-IDF to a CSV...')
    try:
        rows = []
        r_ids = sorted(list([i for i in review_ids if i is not None]))

        # Sort the TF-IDF values and gather their keys.
        sorted_tf_idfs = {}
        regex = re.compile('^[a-zA-Z]+$')
        for r in r_ids:
            temp = dict(sorted(tf_idfs[r].items(), key=operator.itemgetter(1),
                        reverse=True))
            # We only care about a subset of the keys.
            if len(temp.keys()) > 0:
                c = 0
                top_items = []
                for j, k in temp.items():
                    if regex.search(j) is not None and c < top:
                        top_items.append((j, k))
                        c += 1
                sorted_tf_idfs[r] = dict(top_items)

                del temp
                del top_items
                gc.collect()

        # Merge the dictionaries so we can get max value for each token.
        top_kv = merge_dicts([v for k, v in sorted_tf_idfs.items()])

        # Sort the tokens by highest-lowest value.
        top_tokens = OrderedDict(sorted(top_kv.items(),
                                 key=operator.itemgetter(1), reverse=True))

        # Enumerate the tokens to ensure that order is maintained when writing
        # to the CSV file.
        tokens_dict = {t:i for (i, t) in enumerate(top_tokens.keys())
                       if i < top}

        del top_tokens
        del top_kv
        del sorted_tf_idfs
        gc.collect()

        directory = TFIDF_TOKENS_PATH
        if use_lemma:
            directory = TFIDF_LEMMAS_PATH
        with open(directory, 'a', newline='') as f:
            wr = csv.writer(f, delimiter=',', quotechar='/',
                            quoting=csv.QUOTE_MINIMAL)
            wr.writerow(['review_id'] + list(tokens_dict.keys()))

            rows = []
            for r in r_ids:
                row = ['']*len(tokens_dict.keys())
                for tok, val in tf_idfs[r].items():
                    if tok in tokens_dict.keys() and tok in tf_idfs[r].keys():
                        row[tokens_dict[tok]] = round(tf_idfs[r][tok], DECIMAL_PLACES)

                row = [r] + row
                rows.append(row)
                if len(rows) == 200:
                    wr.writerows(rows)
                    logger.warning('Collecting garbage...')
                    rows = []
                    gc.collect()

            # Write any remaining entries to the CSV.
            wr.writerows(rows)

        return True
    except Exception as e:
        logger.error(e)
        traceback.print_exc()
        return False

def get_idf_dict(df, pop_num_docs, use_lemma=False):
    """
    Calculate the IDF for every token in the population.

    NOTE: At first glance, this may seem like it creates a lot of overhead, but
    at the end of the day, it really doesn't.
    """
    idf = dict()
    text = 'token'
    if use_lemma:
        text = 'lemma'
    for item in df:
        (_term, _df) = (item[text], item['df'])
        idf[_term] = math.log(float(pop_num_docs / _df))

    return idf

def load_tfidf_dict(review_ids, idf_dict, num_procs=8, use_lemma=False):
    """
    Call the multiprocessed commands for computing TF-IDF, and return the
    resulting nested dictionary of the form:

    {review_id:{token:score,...},...}
    """
    logger.info('Calculating TF-IDF for {:,} reviews...'
                .format(len(review_ids)))

    tf_idfs = tfidf.compute(review_ids, idf_dict, num_procs, use_lemma)

    return tf_idfs

def get_random_sample(population, pop_review_ids, rand):
    sample_review_ids = []

    neutral = query_rIDs_neutral()
    fixed = query_rIDs_fixed()
    missed = query_rIDs_missed()

    if population == 'all':
        sample_review_ids += query_rIDs_random(neutral, rand)
        sample_review_ids += query_rIDs_random(fixed, rand)
        sample_review_ids += query_rIDs_random(missed, rand)
    elif population == 'fm':
        sample_review_ids += query_rIDs_random(fixed, rand)
        sample_review_ids += query_rIDs_random(missed, rand)
    elif population == 'nf':
        sample_review_ids += query_rIDs_random(neutral, rand)
        sample_review_ids += query_rIDs_random(fixed, rand)
    elif population == 'nm':
        sample_review_ids += query_rIDs_random(neutral, rand)
        sample_review_ids += query_rIDs_random(missed, rand)
    else:
        sample_review_ids += query_rIDs_random(pop_review_ids, rand)

    del neutral
    del fixed
    del missed
    gc.collect()

    return sample_review_ids

#@Field.register_lookup
#class InList(Lookup):
#    lookup_name = 'inlist'
#    function = 'INLIST'
#
#    def as_sql(self, compiler, connection):
#        logger.warning('HI!')
#        lhs, lhs_params = self.process_lhs(compiler, connection)
#        rhs, rhs_params = self.process_rhs(compiler, connection)
#        logger.warning(lhs)
#        logger.warning(lhs_params)
#        print(type(lhs_params))
#        logger.warning(rhs)
#        logger.warning(rhs_params)
#        print(type(rhs_params))
#        params = lhs_params + list(rhs_params)
#        return '(%s) IN %s' % (lhs, rhs), params


#@Field.register_lookup
class AnyLookup(lookups.In):
    def get_rhs_op(self, connection, rhs):
        logger.warning('How did I get here?')
        return '= ANY(ARRAY(%s))' % rhs


class Command(BaseCommand):
    """ Sets up the command line arguments. """

    help = 'Calculate and display the tf-idf score for a single code review ' \
           ' or all code reviews created in a specified year.'

    def add_arguments(self, parser):
        """
        """
        parser.add_argument(
                '--lemma', default=False, action='store_true',
                help='If included, TF-IDF will be calculated on lemmas instead '
                'of tokens.')
        parser.add_argument(
                '--pop', type=str, default='all', choices=['all', 'fixed',
                'missed', 'fm', 'nf', 'nm', '2008', '2009', '2010', '2011',
                '2012', '2013', '2014', '2015', '2016', 'random', 'neutral'],
                help='If unspecified, TF-IDF will be calculated against the '
                'entire corpus of reviews.')
        parser.add_argument(
                '--save', default=False, action='store_true',
                help='If included, save the TF-IDF scores to a CSV file. Else, '
                'print the results to stdout.')
        parser.add_argument(
                '--round', type=int, default=100, help="If specified, TF-IDF "
                "scores will be rounded to the given number of decimal "
                "places. The default is 100 (don't round).")
        parser.add_argument(
                '--top', type=int, default=-1, help='If specified, TF-IDF '
                'will only be calculated for the most frequent number of '
                'tokens provided. The default is to calculate for all '
                'tokens.')
        parser.add_argument(
                '--rand', type=int, default=-1, help='If specified, a random '
                'sampling of the given size will be printed to stdout or '
                'saved to disk.')

    def handle(self, *args, **options):
        global TF_IDFS, DECIMAL_PLACES

        # Grab the command line arguments.
        use_lemma = options.get('lemma', False)
        population = options.get('pop', 'all')
        save = options.get('save', False)
        DECIMAL_PLACES = options.get('round', 100)
        top = options.get('top', -1)
        rand = options.get('rand', -1)

        # Start the timer.
        start = dt.now()
        try:
            logger.info('Gathering review IDs...')
            pop_review_ids = None
            pop_review_ids = query_rIDs(population)

            pop_num_docs = len(pop_review_ids)
            logger.info('Gathered %i review IDs!' % (pop_num_docs))

            sample_review_ids = pop_review_ids
            if rand > 0:
                sample_review_ids = get_random_sample(population,
                                                      pop_review_ids, rand)

            sample_num_docs = len(sample_review_ids)

            logger.info('Calculating the denominator of IDF...')
            df = query_DF(pop_review_ids, use_lemma)

            logger.info('Calculating IDF...')
            idf = get_idf_dict(df, pop_num_docs, use_lemma)

            # This is a hack. It closes all connections before running
            # parallel computations.
            connections.close_all()

            # Calculate the TF-IDF values and store them in the global: TF_IDFS.
            TF_IDFS = load_tfidf_dict(sample_review_ids, idf, 8, use_lemma)

            del idf
            gc.collect()

            if save:
                to_csv(sample_review_ids, TF_IDFS, use_lemma, top)
            else:
                print(TF_IDFS)

            assert len(TF_IDFS) == sample_num_docs
        except KeyboardInterrupt:
            logger.warning('Attempting to abort...')
        finally:
            logger.info('Time: {:.2f} minutes.'
                .format(helpers.get_elapsed(start, dt.now())))
