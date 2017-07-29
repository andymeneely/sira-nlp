"""
@AUTHOR: nuthanmunaiah
"""

import multiprocessing
import json

from datetime import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection, connections

from app.lib import loaders, taggers
from app.lib.helpers import *
from app.lib.logger import *
from app.models import *


class Command(BaseCommand):
    """
    Sets up command line arguments.
    """
    help = 'Tag comments in the database with review experience metrics.'

    def add_arguments(self, parser):
        parser.add_argument(
                '--processes', dest='processes', type=int,
                default=settings.CPU_COUNT,
                help='Number of processes to spawn. Default is {}'.format(
                        settings.CPU_COUNT
                    )
            )
        parser.add_argument(
                '--year', type=int, default=None, dest='year',
                help='Evaluate uncertainty of those code reviews that were '
                'created in the specified year.'
            )

    def handle(self, *args, **options):
        processes = options['processes']
        year = options['year']

        begin = dt.now()
        try:
            comments = Comment.objects.all()
            if year is not None:
                review_ids = Review.objects                      \
                                   .filter(created__year=year)   \
                                   .values_list('id', flat=True)
                comments = Comment.objects                             \
                    .filter(by_reviewer=True)                          \
                    .filter(patch__patchset__review_id__in=review_ids)
            comments = comments.iterator()

            connections.close_all()  # Hack
            tagger = taggers.ExperienceTagger(settings, processes, comments)
            tagger.tag()
        except KeyboardInterrupt:
            warning('Attempting to abort.')
        finally:
            info('Time: {:.2f} mins'.format(get_elapsed(begin, dt.now())))
