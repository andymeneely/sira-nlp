"""
@AUTHOR: meyersbs
"""

import csv
import glob
import operator
import os

from datetime import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from app.lib.files import *
from app.lib.helpers import *
from app.lib.logger import *
from app.lib.rietveld import *

def display_tfidf_score(review, score):
    pass

def display_tfidf_score(review, score):
    pass

def display_review_stats(stats):
    """
    Formats and prints the specified review statistics.
    """
    info('  Status      {}'.format(stats['status']))
    info('  Created On  {}'.format(stats['created']))
    info('  # Reviewers {}'.format(stats['reviewers']))
    info('  # Messages  {}'.format(stats['messages']))
    info('  # Patchsets {}'.format(stats['patchsets']))


def display_reviews_stats(stats):
    """
    Formats and prints the specified review statitics for multiple reviews.
    """
    info('  # Reviews     {}'.format(stats['reviews']))
    info('  # Open        {}'.format(stats['open']))

    info('  Top 10 by # Messages')
    for (key, value) in list(stats['messages'].items())[:10]:
        info('     {:<10} {}'.format(key, value))
    info('  Top 10 by # Comments')
    for (key, value) in list(stats['comments'].items())[:10]:
        info('     {:<10} {}'.format(key, value))
    info('  Top 10 by # Patchsets')
    for (key, value) in list(stats['patchsets'].items())[:10]:
        info('     {:<10} {}'.format(key, value))


class Command(BaseCommand):
    """
    Sets up the command line arguments.
    """
    help = 'Calculate and display the tf-idf score for a single code review ' \
           ' or all code reviews created in a specified year.'

    def add_arguments(self, parser):
        """

        """
        parser.add_argument(
                '-id', type=int, default=None, help='Code review identifier '
                'of a code review to calculate tf-idf.'
            )
        parser.add_argument(
                '-year', type=int, default=None, help='tf-idf of all code '
                'reviews created in the specified year will be aggregated. '
                'Argument is ignored when id is specified.'
            )
        parser.add_argument(
                'term', type=str, default=None, help='The term to calculate '
                'tf-idf for.'
            )

    def handle(self, *args, **options):
        """

        """
        id = options.get('id', None)
        year = options.get('year', None)
        term = options.get('term', None)

        if term is None:
            raise CommandError('term must be specified')

        if id is None and year is None:
            raise CommandError('id or year must be provided')

        begin = dt.now()
        files = Files(settings)
        reviews = {}
        try:
            if id is not None:
                reviews[id] = {}
            else:
                reviews[id] = {}

        except KeyboardInterrupt:
            warning('Attempting to abort.')
        finally:
            info('Time: {:.2f} mins'.format(get_elapsed(begin, dt.now())))
