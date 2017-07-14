"""
@AUTHOR: nuthanmunaiah
"""

import csv
import json
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
    help = 'Retrieve and save code reviews in their JSON format.'

    def add_arguments(self, parser):
        """

        """
        parser.add_argument(
                '-p', type=int, dest='processes', default=6, help='Number of '
                'processes to spawn when running in parallel. Default is 6.'
            )
        parser.add_argument(
                '-s', type=int, dest='chunksize', default=5000,
                help='Maximum number of reviews per file before a new (chunk) '
                'file is created. Default is 5000.'
            )
        parser.add_argument(
                'year', type=int, help='Restrict the retrieval to only those '
                'code reviews that were created in the specified year.'
            )

    def handle(self, *args, **options):
        """

        """
        processes = options['processes']
        year = options['year']
        chunksize = options['chunksize']

        begin = dt.now()
        rietveld = Rietveld()
        files = Files(settings)
        try:
            ids = files.get_ids(year, switch='reviews')
            chunks = list(chunk(ids, chunksize))
            for (i, chnk) in enumerate(chunks):
                (reviews, errors) = rietveld.get_reviews(chnk, processes)
                debug('[Chunk {}/{}] {} reviews and {} errors'.format(
                        (i + 1), len(chunks), len(reviews), len(errors)
                    ))
                files.save_reviews(year, (i + 1), reviews, errors)
            info('Code reviews written to {} file(s) in {}'.format(
                    len(chunks), files.get_reviews_path(year)
                ))
        except KeyboardInterrupt:
            warning('Attempting to abort.')
        finally:
            info('Time: {:.2f} mins'.format(get_elapsed(begin, dt.now())))
