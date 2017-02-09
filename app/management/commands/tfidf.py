"""
@AUTHOR: meyersbs
"""

import json

from datetime import datetime as dt
from math import log10

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.db.models import Count, lookups, Lookup
from django.db.models.fields import Field

from app.lib import helpers, logger
from app.lib.nlp.lemmatizer import Lemmatizer
from app.models import *
from app.queryStrings import *


@Field.register_lookup
class AnyLookup(lookups.in):
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
                '2013', '2014', '2015', '2016'], help='If unspecified, TF-IDF '
                'will be calculated against the entire corpus of reviews. ')

    def handle(self, *args, **options):
        use_lemma = options.get('lemma', False)
        population = options.get('pop', 'all')
        start = dt.now()
        try:
            review_ids = None
            review_ids = query_rIDs(population)

            df = query_DF(review_ids, use_lemma)

            num_documents = review_ids.count()

            idf = dict()
            for item in df:
                (_token, _df) = (item['token'], item['df'])
                idf[_token] = math.log(float(num_documents / _df)

            # This is a hack. It closes all connections before running
            # parallel computations.
            connections.close_all()

            logger.info('Calculating TF-IDF for {:,} reviews...'
                .format(num_documents))
            tfidfs = tfidf.compute(review_ids, idf, num_procs=8, use_lemma)
            assert len(tfidfs) == num_documents
        except KeyboardInterrupt:
            logger.warning('Attempting to abort.')
        finally:
            logger.info('Time: {:.2f} minutes.'
                .format(helpers.get_elapsed(start, dt.now())))
