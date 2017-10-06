"""
@AUTHOR: nuthanmunaiah
"""

import csv
import os

from datetime import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand

from app.lib.files import *
from app.lib.helpers import *
from app.lib.logger import *
from app.lib.rietveld import *


class Command(BaseCommand):
    """
    Sets up command line arguments.
    """
    help = 'Retrieve and save the unique identifier assigned to all ' \
           'Chromium code reviews from Google\'s instance of Rietveld.'

    def add_arguments(self, parser):
        """

        """
        parser.add_argument(
                'year', type=int, help='Restrict the search to retrieve only '
                'those code reviews that were created in the specified year.'
            )

    def handle(self, *args, **options):
        """

        """
        year = options['year']

        begin = dt.now()
        rietveld = Rietveld()
        files = Files(settings)
        try:
            ids = rietveld.get_ids(year)
            filepath = files.save_ids(year, ids, switch='reviews')
            info('Code review identifiers written to {}'.format(filepath))
        except KeyboardInterrupt:
            warning('Attempting to abort.')
        finally:
            info('Time: {:.2f} mins'.format(get_elapsed(begin, dt.now())))
