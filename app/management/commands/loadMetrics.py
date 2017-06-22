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
from app.queryStrings import *


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
                '--metrics', type=list, nargs='+', dest='metrics', default=[None],
                choices=['formality', 'informativeness', 'implicature'],
                help='Specify which metrics to load into the database.'
            )

    def handle(self, *args, **options):
        """

        """
        processes = options['processes']
        metrics = options['metrics']
        begin = dt.now()
        try:
            sents = Sentence.objects.exclude(text='').iterator()
            connections.close_all()
            if 'formality' in metrics:
                try:
                    tagger = taggers.FormalityTagger(settings, processes, sents)
                    tagger.tag()
                except Exception as e: # pragma: no cover
                    warning('Error in formality tagging.')
                    extype, exvalue, extrace = sys.exc_info()
                    traceback.print_exception(extype, exvalue, extrace)
            if 'informativeness' in metrics:
                try:
                    tagger = taggers.InformativenessTagger(settings, processes, sents)
                    tagger.tag()
                except Exception as e: # pragma: no cover
                    warning('Error in informativeness tagging.')
                    extype, exvalue, extrace = sys.exc_info()
                    traceback.print_exception(extype, exvalue, extrace)
            if 'implicature' in metrics:
                try:
                    tagger = taggers.ImplicatureTagger(settings, processes, sents)
                    tagger.tag()
                except Exception as e: # pragma: no cover
                    warning('Error in implicature tagging.')
                    extype, exvalue, extrace = sys.exc_info()
                    traceback.print_exception(extype, exvalue, extrace)
        except KeyboardInterrupt: # pragma: no cover
            warning('Attempting to abort.')
        finally:
            info('Time: {:.2f} mins'.format(get_elapsed(begin, dt.now())))
