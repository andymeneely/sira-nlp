"""
@AUTHOR: nuthanmunaiah
"""

import multiprocessing

from datetime import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection, connections

from app.lib import loaders
from app.lib.helpers import *
from app.lib.logger import *
from app.models import *

import app.queryStrings as qs

class Command(BaseCommand):
    """
    Sets up command line arguments.
    """
    help = "Load the sentence table's 'clean_text' column with truncated " \
           "code tokens."

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
                '--year', dest='year', type=int, default=0, choices=[2008,
                2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016],
                help='If specified, only the given year will be loaded.'
            )

    def handle(self, *args, **options):
        """

        """
        processes = options['processes']
        year = options['year']
        begin = dt.now()
        try:
            if year != 0:
                settings.YEARS = [year]

            if year != 0:
                ids = qs.query_by_year(year, 'sentence', True)
            else:
                ids = qs.query_all('sentence', True)
            connections.close_all()  # Hack

            # Cleaned Sentences
            loader = loaders.SourceCodeSentenceLoader(settings, processes, ids)
            count = loader.load()
            info('  {:,} source code sentences loaded'.format(count))
        except KeyboardInterrupt: # pragma: no cover
            warning('Attempting to abort.')
        finally:
            info('Time: {:.2f} mins'.format(get_elapsed(begin, dt.now())))
