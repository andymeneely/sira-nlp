"""
@AUTHOR: meyersbs
"""

import math
import numpy
import csv
import gc
import random

from datetime import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.db.models import Count, lookups, Lookup
from django.db.models.fields import Field

from app import TFIDF_TOKENS_PATH, TFIDF_LEMMAS_PATH
from app.lib import helpers, logger
from app.lib.nlp import tfidf
from app.lib.nlp.lemmatizer import Lemmatizer
from app.models import *
from app.queryStrings import *


ALL_TOKENS = list()
TF_IDFS = None
DECIMAL_PLACES = 100

def tfidf_to_csv(review_ids, tf_idfs, use_lemma):
    """ Convert the given TF-IDF dictionary to a CSV and write to disk. """
    global ALL_TOKENS, DECIMAL_PLACES
    try:
        tokens_dict = {t:i for (i, t) in enumerate(ALL_TOKENS)}
        rows = []
        review_ids = [i for i in review_ids if i is not None]
        r_ids = sorted(list(review_ids))

        directory = TFIDF_TOKENS_PATH
        if use_lemma:
            directory = TFIDF_LEMMAS_PATH
        with open(directory, 'a', newline='') as f:
            wr = csv.writer(f, delimiter=',', quotechar='/',
                            quoting=csv.QUOTE_MINIMAL)
            wr.writerow(['review_id'] + list(tokens_dict.keys()))

            c = 0
            rows = []
            for r in r_ids:
                row = ['']*len(ALL_TOKENS)
                for tok, val in tf_idfs[r].items():
                    if tok in tokens_dict.keys():
                        row[tokens_dict[tok]] = round(val, DECIMAL_PLACES)

                row = [r] + row
                rows.append(row)
                if len(rows) == 200:
                    wr.writerows(rows)
                    logger.warning('Collecting garbage...')
                    rows = []
                    gc.collect()
                c += 1

            # Write any remaining entries to the CSV.
            wr.writerows(rows)

        return True
    except Exception as e:
        logger.error(e)
        return False

# For some strange reason, moving these operations into their own functions
# causes bizarre errors.
def get_idf_dict(df, num_docs):
    return False
    idf = dict()
    for item in df:
        (_token, _df) = (item['token'], item['df'])
        idf[_token] = math.log(float(num_docs / _df))

    return idf

def load_tfidf_dict(review_ids, idf_dict, num_procs=8, use_lemma=False):
    return False
    logger.info('Calculating TF-IDF for {:,} reviews...'
                .format(len(review_ids)))

    tf_idfs = tfidf.compute(review_ids, idf_dict, num_procs, use_lemma)

    return tf_idfs

@Field.register_lookup
class AnyLookup(lookups.In):
    def get_rhs_op(self, connection, rhs):
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
                '--group', type=str, default='pop', choices=['pop', 'fixed',
                'missed', 'neutral', 'fm', 'nf', 'nm'], help='If specified, '
                'only reviews within the population and matching the group '
                'will be printed to stdout or saved to disk.')
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
        global ALL_TOKENS, TF_IDFS, DECIMAL_PLACES

        # Grab the command line arguments.
        use_lemma = options.get('lemma', False)
        population = options.get('pop', 'all')
        save = options.get('save', False)
        DECIMAL_PLACES = options.get('round', 100)
        top = options.get('top', -1)
        group = options.get('group', 'pop')
        rand = options.get('rand', -1)

        # Start the timer.
        start = dt.now()
        try:
            logger.info('Gathering review IDs...')
            pop_review_ids = None
            pop_review_ids = query_rIDs(population)

            group_review_ids = None
            if group == 'pop':
                group_review_ids = pop_review_ids
            else:
                group_review_ids = query_rIDs(group)

            try:
                pop_num_docs = pop_review_ids.count()
            except (AttributeError, TypeError) as e:
                print(e)
                pop_num_docs = len(pop_review_ids)
            print(pop_num_docs)

            try:
                group_num_docs = group_review_ids.count()
            except (AttributeError, TypeError) as e:
                print(e)
                group_num_docs = len(group_review_ids)
            print(group_num_docs)

            if top <= 0:
                logger.info('Gathering all tokens...')
                ALL_TOKENS = query_tokens(pop_review_ids, use_lemma)
            else:
                logger.info('Gathering the %i most frequent tokens...' %
                    (top))
                ALL_TOKENS = query_top_x_tokens(pop_review_ids, top, use_lemma)
                print(ALL_TOKENS)

            if rand > 0:
                sample_indices = []
                for i in range(rand):
                    sample_indices.append(random.randint(0, group_num_docs))

                sample_reviews = [group_review_ids[i] for i in sample_indices]
                group_review_ids = sample_reviews
                group_num_docs = len(group_review_ids)

            logger.info('Calculating the denominator of IDF...')
            df = query_DF(pop_review_ids, use_lemma)

            logger.info('Calculating IDF...')
            idf = dict()
            if use_lemma:
                for item in df:
                    (_lemma, _df) = (item['lemma'], item['df'])
                    idf[_lemma] = math.log(float(pop_num_docs / _df))
            else:
                for item in df:
                    (_token, _df) = (item['token'], item['df'])
                    idf[_token] = math.log(float(pop_num_docs / _df))


            # This is a hack. It closes all connections before running
            # parallel computations.
            connections.close_all()

            # Calculate the TF-IDF values and store them in the global: TF_IDFS.
            logger.info('Calculating TF-IDF for {:,} reviews...'
                        .format(group_num_docs))
            TF_IDFS = tfidf.compute(group_review_ids, idf, 8, use_lemma)

            if save:
                logger.info('Saving TF-IDF to a CSV...')
                tfidf_to_csv(group_review_ids, TF_IDFS, use_lemma)
            else:
                print(TF_IDFS)

            assert len(TF_IDFS) == group_num_docs
        except KeyboardInterrupt:
            logger.warning('Attempting to abort...')
        finally:
            logger.info('Time: {:.2f} minutes.'
                .format(helpers.get_elapsed(start, dt.now())))
