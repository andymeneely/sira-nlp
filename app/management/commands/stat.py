"""
@AUTHOR: nuthanmunaiah
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
    help = 'Display statistics about single code review or all code reviews ' \
           'created in a specified year.'

    def add_arguments(self, parser):
        """

        """
        parser.add_argument(
                '-id', type=int, default=None, help='Code review identifier '
                'of a code review the statistics of which will be displayed.'
            )
        parser.add_argument(
                '-year', type=int, default=None, help='Statistics of all code'
                'reviews created in the specified year will be aggregated. '
                'Argument is ignored when id is specified.'
            )

    def handle(self, *args, **options):
        """

        """
        id = options.get('id', None)
        year = options.get('year', None)

        if id is None and year is None:
            raise CommandError('id or year must be provided')

        begin = dt.now()
        files = Files(settings)
        try:
            if id is not None:
                info('{}'.format(id))
                display_review_stats(files.stat_review(id))
            else:
                info('{}'.format(year))
                display_reviews_stats(files.stat_reviews(year))
        except KeyboardInterrupt:
            warning('Attempting to abort.')
        finally:
            info('Time: {:.2f} mins'.format(get_elapsed(begin, dt.now())))
