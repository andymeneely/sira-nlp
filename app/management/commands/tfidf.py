"""
@AUTHOR: meyersbs
"""

import math
import numpy
import csv

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
TF_IDFS = dict()

def tfidf_to_csv(review_ids, tf_idfs):
    global ALL_TOKENS
    try:
        tokens_dict = {t:i for (i, t) in enumerate(ALL_TOKENS)}
        rows = []
        r_ids = sorted(list(review_ids))
        for r in r_ids:
            row = ['']*len(ALL_TOKENS)
            for tok, val in tf_idfs[r].items():
                row[tokens_dict[tok]] = val

            row = [r] + row
            rows.append(row)

        with open(TFIDF_TOKENS_PATH, 'w', newline='') as f:
            wr = csv.writer(f, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
            header_row = ['review_id'] + list(tokens_dict.keys())
            wr.writerow(header_row)
            wr.writerows(rows)

        return True
    except Exception:
        return False

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
                'missed', 'fixmiss', '2008', '2009', '2010', '2011', '2012',
                '2013', '2014', '2015', '2016', 'random'], help='If '
                'unspecified, TF-IDF will be calculated against the entire '
                'corpus of reviews. ')

    def handle(self, *args, **options):
        global TF_IDFS, ALL_TOKENS
        use_lemma = options.get('lemma', False)
        population = options.get('pop', 'all')
        start = dt.now()
        try:
            review_ids = None
            review_ids = query_rIDs(population)
            print(review_ids)
            ALL_TOKENS = query_tokens(review_ids)
            df = query_DF(review_ids, use_lemma)

            try:
                num_documents = review_ids.count()
            except AttributeError:
                num_documents = len(review_ids)
            except TypeError:
                num_documents = len(review_ids)

            idf = dict()
            for item in df:
                (_token, _df) = (item['token'], item['df'])
                idf[_token] = math.log(float(num_documents / _df))

            # This is a hack. It closes all connections before running
            # parallel computations.
            connections.close_all()

            logger.info('Calculating TF-IDF for {:,} reviews...'
                .format(num_documents))

            TF_IDFS = tfidf.compute(review_ids, idf, 8, use_lemma)
            tfidf_to_csv(review_ids, TF_IDFS)

            assert len(TF_IDFS) == num_documents
        except KeyboardInterrupt:
            logger.warning('Attempting to abort.')
        finally:
            logger.info('Time: {:.2f} minutes.'
                .format(helpers.get_elapsed(start, dt.now())))
