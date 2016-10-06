import csv
import json
import os

from datetime import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand

from app.lib.helpers import *
from app.lib.logger import *
from app.lib.rietveld import *


def _save(reviews, errors, directory, index):
    if not os.path.exists(directory):
        debug('Creating {}'.format(directory))
        os.mkdir(directory, mode=0o755)

    path = os.path.join(directory, 'reviews.{}.json'.format(index))
    with open(path, 'w') as file:
        json.dump(reviews, file)

    if errors:
        path = os.path.join(directory, 'errors.csv'.format(index))
        with open(path, 'a') as file:
            writer = csv.writer(file)
            writer.writerows([(error,) for error in errors])


def _get_ids(year, directory):
    ids = None
    path = os.path.join(directory, '{}.csv'.format(year))
    debug('Getting Rietveld IDs from {}'.format(path))
    with open(path, 'r') as file:
        reader = csv.reader(file)
        ids = [row[0] for row in reader]
    return ids


class Command(BaseCommand):
    help = 'Retrieve and save code reviews in their JSON format.'

    def add_arguments(self, parser):
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
        processes = options['processes']
        year = options['year']
        chunksize = options['chunksize']

        directory = settings.REVIEWS_PATH.format(year=year)

        begin = dt.now()
        rietveld = Rietveld()
        try:
            ids = _get_ids(year, settings.IDS_PATH)
            ids_chunks = list(chunk(ids, chunksize))
            index = 0
            for ids_chunk in ids_chunks:
                index += 1
                (reviews, errors) = rietveld.get_reviews(ids_chunk, processes)
                debug('[Chunk {}/{}] {} reviews and {} errors'.format(
                        index, len(ids_chunks), len(reviews), len(errors)
                    ))
                _save(reviews, errors, directory, index)
            info('Code reviews written to {} file(s) in {}'.format(
                    len(ids_chunks), directory
                ))
        except KeyboardInterrupt:
            warning('Attempting to abort.')
        finally:
            info('Time: {:.2f} mins'.format(get_elapsed(begin, dt.now())))
