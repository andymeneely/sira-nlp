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
                #choices=['formality', 'informativeness', 'implicature'],
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
            sentences = []
            if year != 0:
                sentences = qs.query_by_year(year, 'sentence', ids=False).exclude(text='')
            else:
                sentences = qs.query_all('sentence', ids=False).exclude(text='')
            connections.close_all()
            tagger = taggers.MetricsCleanTagger(settings, processes, sentences, metrics)
            tagger.tag()
        except KeyboardInterrupt: # pragma: no cover
            warning('Attempting to abort.')
        finally:
            info('Time: {:.2f} mins'.format(get_elapsed(begin, dt.now())))
