"""
@AUTHOR: meyersbs
"""

import multiprocessing
import json
import sys
import traceback

from datetime import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection, connections
from django.db.models import Q

from app.lib import loaders, taggers
from app.lib.helpers import *
from app.lib.logger import *
from app.models import *

import app.queryStrings as qs

class Command(BaseCommand):
    """
    Sets up command line arguments.
    """
    help = 'Load the database with various metrics.'

    def add_arguments(self, parser):
        """

        """
        parser.add_argument(
                '--processes', dest='processes', type=int,
                default=settings.CPU_COUNT,
                help='Number of processes to spawn. Default is {}'.format(
                        settings.CPU_COUNT
                    )
            )
        parser.add_argument(
                '--metrics', type=str, nargs='+', dest='metrics', default=[None],
                #choices=['sent_length', 'type_token_ratio', 'pronoun_density',
                #         'flesch-kincaid', 'stop_word_ratio', 'question_ratio',
                #         'conceptual_similarity']
                help='Specify which metrics to load into the database.'
            )
        parser.add_argument(
                '--year', type=int, dest='year', default=0, choices=[2008,
                2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 0],
                help='If specified, only sentences in the given year will be'
                'tagged with the given "--metrics".'
            )

    def handle(self, *args, **options):
        """

        """
        processes = options['processes']
        metrics = options['metrics']
        year = options['year']
        begin = dt.now()
        try:
            #print(len(qs.query_by_year(year, 'token', ids=True)))
            tokens = []
            if year != 0:
                tokens = qs.query_by_year(year, 'token', ids=False).exclude(token='').iterator()
            else:
                tokens = qs.query_all('token', ids=False).exclude(token='').iterator()
            connections.close_all()
            #print(tokens)
            tagger = taggers.SourceCodeTagger(settings, processes, tokens)
            total = tagger.tag()
            #print(total)
        except KeyboardInterrupt: # pragma: no cover
            warning('Attempting to abort.')
        finally:
            info('Time: {:.2f} mins'.format(get_elapsed(begin, dt.now())))
