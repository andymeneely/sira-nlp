from datetime import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand

from app.lib import loaders, taggers
from app.lib.helpers import *
from app.lib.logger import *


class Command(BaseCommand):
    help = 'Load the database with code review and bug information.'

    def handle(self, *args, **options):
        begin = dt.now()
        try:
            info('loaddb Command')
            info('  Years: {}'.format(settings.YEARS))

            loader = loaders.BugLoader(settings)
            count = loader.load()
            info('  {} bugs loaded'.format(count))
            loader = loaders.VulnerabilityLoader(settings)
            count = loader.load()
            info('  {} vulnerabilities loaded'.format(count))
            loader = loaders.ReviewLoader(settings)
            count = loader.load()
            info('  {} reviews loaded'.format(count))

            tagger = taggers.MissedVulnerabilityTagger(settings)
            count = tagger.tag()
            info('  {} reviews tagged as missed a vulnerability'.format(count))
        except KeyboardInterrupt:
            warning('Attempting to abort.')
        finally:
            info('Time: {:.2f} mins'.format(get_elapsed(begin, dt.now())))
