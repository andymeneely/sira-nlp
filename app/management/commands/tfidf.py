"""
@AUTHOR: meyersbs
"""

import math
import numpy
import csv
import gc

from datetime import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.db.models import Count, lookups, Lookup
from django.db.models.fields import Field

from app import TFIDF_TOKENS_PATH
from app.lib import helpers, logger
from app.lib.nlp import tfidf
from app.lib.nlp.lemmatizer import Lemmatizer
from app.models import *
from app.queryStrings import *


ALL_TOKENS = list()
TF_IDFS = None
DECIMAL_PLACES = 100

def tfidf_to_csv(review_ids, tf_idfs):
    global ALL_TOKENS, DECIMAL_PLACES
    try:
        tokens_dict = {t:i for (i, t) in enumerate(ALL_TOKENS)}
        rows = []
        review_ids = [i for i in review_ids if i is not None]
        r_ids = sorted(list(review_ids))
        with open(TFIDF_TOKENS_PATH, 'a', newline='') as f:
#            print('First')
            wr = csv.writer(f, delimiter=',', quotechar='|',
                            quoting=csv.QUOTE_MINIMAL)
            header_row = ['review_id'] + list(tokens_dict.keys())
            wr.writerow(header_row)
#            print('Second')

            c = 0
            rows = []
            for r in r_ids:
#                print('Third')
                row = ['']*len(ALL_TOKENS)
                for tok, val in tf_idfs[r].items():
#                    print('Fourth ' + tok)
                    if tok in tokens_dict.keys():
                        row[tokens_dict[tok]] = round(val, DECIMAL_PLACES)
#                    print('Fifth')

                row = [r] + row
                rows.append(row)
#                print('Sixth ' + str(c))
                if len(rows) == 200:
#                    print('Seventh')
                    wr.writerows(rows)
                    logger.warning('Collecting garbage...')
                    rows = []
                    gc.collect()
#                print('Eighth')
                c += 1

            # Write any remaining entries to the CSV.
#            print('Ninth')
            wr.writerows(rows)
#            print('Tenth')

        return True
    except Exception as e:
        logger.error(e)
        return False

# For some strange reason, moving these operations into their own functions
# causes bizarre errors.
def get_idf_dict(df, num_docs):
    """
    """
    return False
    idf = dict()
    for item in df:
        (_token, _df) = (item['token'], item['df'])
        idf[_token] = math.log(float(num_docs / _df))

    return idf

def load_tfidf_dict(review_ids, idf_dict, num_procs=8, use_lemma=False):
    """
    """
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
                '--save', default=False, action='store_true',
                help='If included, save the TF-IDF scores to a CSV file. Else, '
                'print the results to stdout.')
        parser.add_argument(
                '--round', type=int, default=100, help="If specified, TF-IDF "
                "scores will be rounded to the given number of decimal "
                "places. The default is 100 (don't round).")
        parser.add_argument(
                '--top', type=int, default=-1, help='If specified, TF-IDF '
                'will only be calculated for the mose frequent number of '
                'tokens provided. The default is to calculate for all '
                'tokens.')

    def handle(self, *args, **options):
        global ALL_TOKENS, TF_IDFS, DECIMAL_PLACES

        # Grab the command line arguments.
        use_lemma = options.get('lemma', False)
        population = options.get('pop', 'all')
        save = options.get('save', False)
        DECIMAL_PLACES = options.get('round', 100)
        top = options.get('top', -1)

        # Start the timer.
        start = dt.now()
        try:
            logger.info('Gathering review IDs...')
            review_ids = None
            review_ids = query_rIDs(population)

            try:
                num_documents = review_ids.count()
            except (AttributeError, TypeError) as e:
                print(e)
                num_documents = len(review_ids)
            print(num_documents)

            if top <= 0:
                logger.info('Gathering all tokens...')
                ALL_TOKENS = query_tokens(review_ids)
#                print(type(ALL_TOKENS))
            else:
                logger.info('Gathering the %i most frequent tokens...' %
                    (top))
                ALL_TOKENS = query_top_x_tokens(review_ids, top)
#                print(type(ALL_TOKENS))
#                print(ALL_TOKENS)

            logger.info('Calculating the denominator of IDF...')
            df = query_DF(review_ids, use_lemma)

            logger.info('Calculating IDF...')
            idf = dict()
            for item in df:
                (_token, _df) = (item['token'], item['df'])
                idf[_token] = math.log(float(num_documents / _df))


            # This is a hack. It closes all connections before running
            # parallel computations.
            connections.close_all()

            # Calculate the TF-IDF values and store them in the global: TF_IDFS.
            logger.info('Calculating TF-IDF for {:,} reviews...'
                        .format(num_documents))
            TF_IDFS = tfidf.compute(review_ids, idf, 8, use_lemma)
#            for k,v in TF_IDFS.items():
#                print(v)

            if save:
                logger.info('Saving TF-IDF to a CSV...')
                tfidf_to_csv(review_ids, TF_IDFS)
            else:
                print(TF_IDFS)

            assert len(TF_IDFS) == num_documents
        except KeyboardInterrupt:
            logger.warning('Attempting to abort...')
        finally:
            logger.info('Time: {:.2f} minutes.'
                .format(helpers.get_elapsed(start, dt.now())))
