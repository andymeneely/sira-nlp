import csv
import os

from datetime import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand

from app.lib.helpers import *
from app.lib.logger import *
from app.lib.rietveld import *


def _save(ids, year, directory):
    path = os.path.join(directory, '{}.csv'.format(year))
    with open(path, 'a') as file:
        writer = csv.writer(file)
        writer.writerows([(id,) for id in ids])
    return path


class Command(BaseCommand):
    help = 'Retrieve and save the unique identifier assigned to all ' \
           'Chromium code reviews from Google\'s instance of Rietveld.'

    def add_arguments(self, parser):
        parser.add_argument(
                'year', type=int, help='Restrict the search to retrieve only '
                'those code reviews that were created in the specified year.'
            )

    def handle(self, *args, **options):
        year = options['year']

        begin = dt.now()
        rietveld = Rietveld()
        try:
            ids = rietveld.get_ids(year)
            filepath = _save(ids, year, settings.IDS_PATH)
            info('Rietveld IDs written to {}'.format(filepath))
        except KeyboardInterrupt:
            warning('Attempting to abort.')
        finally:
            info('Time: {:.2f} mins'.format(get_elapsed(begin, dt.now())))
