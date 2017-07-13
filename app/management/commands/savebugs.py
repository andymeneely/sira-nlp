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
from app.lib.monorail import *


class Command(BaseCommand):
    help = 'Retrieve and save bugs in their JSON format.'

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
                'bugs that were published in the specified year.'
            )

    def handle(self, *args, **options):
        processes = options['processes']
        year = options['year']
        chunksize = options['chunksize']

        begin = dt.now()
        monorail = Monorail(settings.MONORAIL_URL, settings.GOOGLESA_KEYFILE)
        files = Files(settings)
        try:
            ids = files.get_ids(year, switch='bugs')
            chunks = list(chunk(ids, chunksize))
            for (i, chnk) in enumerate(chunks):
                (bugs, errors) = monorail.get_bugs(chnk, processes)
                debug('[Chunk {}/{}] {} bugs and {} errors'.format(
                        (i + 1), len(chunks), len(bugs), len(errors)
                    ))
                files.save_bugs(year, (i + 1), bugs, errors)
            info('Bugs written to {} file(s) in {}'.format(
                    len(chunks), files.get_bugs_path(year)
                ))
        except KeyboardInterrupt:
            warning('Attempting to abort.')
        finally:
            info('Time: {:.2f} mins'.format(get_elapsed(begin, dt.now())))
