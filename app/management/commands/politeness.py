"""
@AUTHOR: nuthanmunaiah
"""

import multiprocessing
import json

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
    help = 'Load the database with code review and bug information.'

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
                '--pop', type=str, default='all', dest='population',
                choices=['all', 'fixed', 'missed', 'neutral', 'empty'],
                help='The review IDs to repopulate complexity metrics for. '
                "Defualt is 'all'."
            )
        parser.add_argument(
                '--year', type=int, default=0, dest='year', choices=[2008,
                2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016],
                help='If specified, only sentences from this year will be'
                ' tagged with politeness.'
            )

    def handle(self, *args, **options):
        """

        """
        processes = options['processes']
        population = options['population']
        year = options['year']
        begin = dt.now()
        try:
            if year == 0:
                sents = qs.query_all('sentence', ids=False).exclude(text='') \
                          .iterator()
            else:
                sents = qs.query_by_year(year, 'sentence', ids=False).exclude(text='') \
                          .iterator()

            connections.close_all()
            tagger = taggers.PolitenessTagger(settings, processes, sents)
            tagger.tag()

        except KeyboardInterrupt:
            warning('Attempting to abort.')
        finally:
            info('Time: {:.2f} mins'.format(get_elapsed(begin, dt.now())))
