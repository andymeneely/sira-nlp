"""
@AUTHOR: nuthanmunaiah
"""

import multiprocessing
import json

from datetime import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection, connections

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
                '--root', type=str, default='stem', dest='root',
                choices=['stem', 'lemma'], help='Specify whether to use the '
                "token's lemma or stem for classification. Default is 'stem'."
            )
        parser.add_argument(
                '--year', type=int, default=None, dest='year',
                help='Evaluate uncertainty of those code reviews that were '
                'created in the specified year.'
            )

    def handle(self, *args, **options):
        """

        """
        processes = options['processes']
        population = options['population']
        root = options['root']
        year = options['year']
        begin = dt.now()
        try:
            sentences = []
            if year is not None:
                sentences = qs.query_by_year(year, 'sentence', ids=False)
            else:
                sentences = qs.query_all('sentence', ids=False)
            sentences = sentences.iterator()

            connections.close_all()
            tagger = taggers.UncertaintyTagger(
                    settings, processes, sentences, root
                )
            tagger.tag()
        except KeyboardInterrupt:
            warning('Attempting to abort.')
        finally:
            info('Time: {:.2f} mins'.format(get_elapsed(begin, dt.now())))
