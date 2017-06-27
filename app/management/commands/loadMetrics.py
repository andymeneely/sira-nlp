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
        parser.add_argument(
                '--empty', action='store_true', help='If specified, only '
                'sentences that do not already have the given "--metrics" '
                'populated will be tagged.'
            )

    def handle(self, *args, **options):
        """

        """
        processes = options['processes']
        metrics = options['metrics']
        year = options['year']
        empty = options['empty']
        begin = dt.now()
        try:
            if year != 0:
                sentences = Sentence.objects.exclude(text='').filter(message__review__created__year=year)
            else:
                sentences = Sentence.objects.exclude(text='')
            if 'formality' in metrics:
                info("Gathering sentences...")
                if empty:
                    sents = sentences.filter(metrics__contains="{'formality'}:{}}").iterator()
                else:
                    sents = sentences.iterator()
                connections.close_all()
                try:
                    info("Tagging sentences with formality...")
                    tagger = taggers.FormalityTagger(settings, processes, sents)
                    tagger.tag()
                except Exception as e: # pragma: no cover
                    warning('Error in formality tagging.')
                    extype, exvalue, extrace = sys.exc_info()
                    traceback.print_exception(extype, exvalue, extrace)
            if 'informativeness' in metrics:
                info("Gathering sentences...")
                if empty:
                    sents = sentences.filter(metrics__contains="{'informativeness'}:{}}").iterator()
                else:
                    sents = sentences.iterator()
                connections.close_all()
                try:
                    info("Tagging sentences with informativeness...")
                    tagger = taggers.InformativenessTagger(settings, processes, sents)
                    tagger.tag()
                except Exception as e: # pragma: no cover
                    warning('Error in informativeness tagging.')
                    extype, exvalue, extrace = sys.exc_info()
                    traceback.print_exception(extype, exvalue, extrace)
            if 'implicature' in metrics:
                info("Gathering sentences...")
                if empty:
                    sents = sentences.filter(metrics__contains="{'implicature'}:{}}").iterator()
                else:
                    sents = sentences.iterator()
                connections.close_all()
                try:
                    info("Tagging sentences with implicature...")
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
