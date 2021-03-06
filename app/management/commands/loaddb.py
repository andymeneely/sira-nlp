"""
@AUTHOR: nuthanmunaiah
"""

import multiprocessing

from datetime import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection, connections

from app.lib import loaders, taggers
from app.lib.helpers import *
from app.lib.logger import *
from app.models import *

import app.queryStrings as qs

class Command(BaseCommand):
    """
    Sets up command line arguments.
    """
    help = 'Load the database with code review and bug information.'

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
                '--year', dest='year', type=int, default=0, choices=[2008,
                2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016],
                help='If specified, only the given year will be loaded.'
            )

    def handle(self, *args, **options):
        """

        """
        processes = options['processes']
        year = options['year']
        begin = dt.now()
        try:
            info('loaddb Command')
            info('  Years: {}'.format(settings.YEARS))

            if year != 0:
                settings.YEARS = [year]

            loader = loaders.BugLoader(settings, processes)
            count = loader.load()
            info('  {:,} bugs loaded'.format(count))

            loader = loaders.VulnerabilityLoader(settings, processes)
            count = loader.load()
            info('  {:,} vulnerabilities loaded'.format(count))

            loader = loaders.ReviewLoader(settings, processes)
            count = loader.load()
            info('  {:,} reviews loaded'.format(count))

            tagger = taggers.MissedVulnerabilityTagger(settings, processes)
            count = tagger.tag()
            info('  {:,} reviews missed a vulnerability'.format(count))

            if year != 0:
                ids = qs.query_by_year(year, 'review', True)
            else:
                ids = qs.query_all('review', True)
            connections.close_all()  # Hack

            # Comments
            loader = loaders.CommentLoader(settings, processes, ids)
            count = loader.load()
            info('  {:,} comments loaded'.format(count))
            connections.close_all()  # Hack
            loader = loaders.SentenceCommentLoader(settings, processes, ids)
            count = loader.load()
            info('  {:,} sentences loaded'.format(count))
            connections.close_all()  # Hack

            tagger = taggers.UsefulCommentTagger(settings, processes, ids)
            count = tagger.tag()
            info('  {:,} comments were useful'.format(count))

            # Messages
            connections.close_all()  # Hack
            loader = loaders.MessageLoader(settings, processes, ids)
            count = loader.load()
            info('  {:,} messages loaded'.format(count))
            connections.close_all()  # Hack
            loader = loaders.SentenceMessageLoader(settings, processes, ids)
            count = loader.load()
            info('  {:,} sentences loaded'.format(count))
            connections.close_all()  # Hack

            # Tokens
            loader = loaders.TokenLoader(settings, processes, ids)
            count = loader.load()
            info('  {:,} tokens loaded'.format(count))

            with connection.cursor() as cursor:
                cursor.execute('REFRESH MATERIALIZED VIEW {};'.format('vw_review_token'))
                cursor.execute('REFRESH MATERIALIZED VIEW {};'.format('vw_review_lemma'))
        except KeyboardInterrupt: # pragma: no cover
            warning('Attempting to abort.')
        finally:
            info('Time: {:.2f} mins'.format(get_elapsed(begin, dt.now())))
