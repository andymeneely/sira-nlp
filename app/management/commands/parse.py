import ast

from datetime import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from app.lib import helpers
from app.lib.logger import *
from app.models import *


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

        try:
            review = helpers.get_row(Review, id=id)
            if review is None:
                raise CommandError('No review identified by {}'.format(id))
            review = review.document
            print('#' * 72)
            print('# Code Review {}'.format(id))
            print('# Description\n')
            print(format(review['description']))
            print('#' * 72)
            print('# Conversation\n')
            messages = self.get_messages(review, clean=clean)
            for (i, (sender, message)) in enumerate(messages):
                print('-' * 72)
                print('[{}/{}] From {}'.format((i + 1), len(messages), sender))
                print('-' * 72)
                print(message)
            print('#' * 72)
        except KeyboardInterrupt:
            warning('Attempting to abort.')

    def get_messages(self, review, clean=False):
        messages = list()
        for message in review['messages']:
            sender = message['sender']
            if sender in settings.BOTS:
                continue
            text = helpers.clean(message['text']) if clean else message['text']
            messages.append((sender, text))
        return messages
