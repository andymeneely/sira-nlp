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
from app.queryStrings import *


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
                '--zeros', default=False, action='store_true',
                help='If specified, only repopulate complexity metrics '
                'that were previously populated with all zeros.'
            )

    def handle(self, *args, **options):
        """

        """
        processes = options['processes']
        population = options['population']
        zeros = options['zeros']
        begin = dt.now()
        try:
            ids = []
            if zeros:
                ids = query_rIDs_all()
            else:
                pop_ops = {'all': query_rIDs_all,
                           'fixed': query_rIDs_fixed,
                           'missed': query_rIDs_missed,
                           'neutral': query_rIDs_neutral,
                           'empty': query_rIDs_empty,}
                ids = pop_ops[population]()

            connections.close_all()
            tagger = taggers.ComplexityTagger(settings, processes, ids, zeros)
            tagger.tag()

        except KeyboardInterrupt:
            warning('Attempting to abort.')
        finally:
            info('Time: {:.2f} mins'.format(get_elapsed(begin, dt.now())))
