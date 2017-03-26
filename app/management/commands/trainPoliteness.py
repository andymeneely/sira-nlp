"""
@AUTHOR: meyersbs
"""

import glob

from datetime import datetime as dt
from datetime import time

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from app.lib.logger import *
from app.lib.helpers import get_elapsed
from app.lib.external.politeness.scripts.train_model import *

class Command(BaseCommand):
    """
    Sets up the command line arguments.
    """
    help = 'Train the Stanford Politeness Classifier.'

    def add_arguments(self, parser):
        parser.add_argument(
                '--pop', type=str, default='all', choices=['all', 'wikipedia',
                'stackexchange'], help='Train the model using the provided '
                'population.'
            )
        parser.add_argument(
                '--ntesting', type=int, default=500, help='Tell the training'
                'algorithm to withhold this many random documents as the '
                'testing set.'
            )

    def handle(self, *args, **options):
        global ALL_REVIEW_IDS
        population = options.get('pop', 'all')
        ntesting = options.get('ntesting', 500)
        endTime = dt.now()
        try:
            begin = dt.now()
            train_classifier(population, ntesting)
            endTime = dt.now()
        except KeyboardInterrupt:
            warning('Attempting to abort.')
            endTime = dt.now()
        finally:
            info('Time: {:.2f} mins'.format(get_elapsed(begin, endTime)))
