"""
@AUTHOR: meyersbs
"""

import traceback
import sys

from json import JSONDecodeError

from datetime import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.db.models import Count, lookups, Lookup
from django.db.models.fields import Field

from app.lib import helpers, logger, taggers
from app.lib.nlp.complexity import *
from app.models import *

import app.queryStrings as qs

#@Field.register_lookup
class AnyLookup(lookups.In):
    def get_rhs_op(self, connection, rhs):
        return '= ANY(ARRAY(%s))' % rhs

class Command(BaseCommand):
    """ Sets up the command line arguments. """

    help = 'Calculate and display the syntactic complexity scores for a ' \
           'messages within a group of code review.'

    def add_arguments(self, parser):
        """

        """
        parser.add_argument(
                '--processes', dest='processes', type=int,
                default=settings.CPU_COUNT, help='Number of processes to spawn.'
                ' Default is {}'.format(settings.CPU_COUNT)
            )
        parser.add_argument(
                '--condition', type=str, default='all', dest='condition',
                choices=['all', 'empty', 'failed'], help="The sentences to "
                "repopulate parses for. Defualt is 'all'."
            )

    def handle(self, *args, **options):
        """

        """
        processes = options['processes']
        condition = options['condition']
        begin = dt.now()
        try:
            sents = qs.query_all('sentence', ids=False)
            if condition == 'all':
                sents = sents.exclude(text='').iterator()
            elif condition == 'empty' or condition == 'failed':
                sents = sents.filter(metrics__sentiment={}).exclude(text='').iterator()

            connections.close_all()
            tagger = taggers.SentimentTagger(settings, processes, sents)
            tagger.tag()

        except KeyboardInterrupt:
            logger.warning('Attempting to abort...')
        finally:
            logger.info('Time: {:.2f} minutes.'
                .format(helpers.get_elapsed(begin, dt.now())))
