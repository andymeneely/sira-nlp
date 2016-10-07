import csv
import glob
import operator
import os

from datetime import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand

from app.lib.files import *
from app.lib.helpers import *
from app.lib.logger import *
from app.lib.rietveld import *


class Command(BaseCommand):
    help = 'Parse a code review in its JSON form and present the '\
           'conversation in plain text.'

    def add_arguments(self, parser):
        parser.add_argument(
                '--clean', action='store_true', help='Clean-up the code '
                'review messages when parsing.'
            )
        parser.add_argument(
                'id', type=int, default=None, help='Code review identifier '
                'of a code review.'
            )

    def handle(self, *args, **options):
        id = options['id']
        clean = options.get('clean', False)

        files = Files(settings)
        try:
            year = files.get_year(id)
            messages = files.get_messages(id, year, clean=clean)

            print('#' * 72)
            print('# Code Review {}'.format(id))
            print('# Description\n')
            print(format(files.get_description(id, year)))
            print('#' * 72)
            print('# Conversation\n')
            for (i, (sender, message)) in enumerate(messages):
                print('-' * 72)
                print('[{}/{}] From {}'.format((i + 1), len(messages), sender))
                print('-' * 72)
                print(message)
            print('#' * 72)
        except KeyboardInterrupt:
            warning('Attempting to abort.')
