import csv
import glob
import operator
import os

from datetime import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from app.lib.helpers import *
from app.lib.logger import *
from app.lib.rietveld import *


def _get_count(path):
    files = glob.glob(os.path.join(path, 'reviews.*.json'))
    return len(files)


def _get_review(id, year):
    review = None
    directory = settings.REVIEWS_PATH.format(year=year)
    for index in range(1, _get_count(directory)):
        path = os.path.join(directory, 'reviews.{}.json'.format(index))
        debug(path)
        with open(path, 'r') as file:
            reviews = json.load(file)
            for review in reviews:
                if id == review['issue']:
                    return review
    return review


def _get_reviews(year):
    reviews = None
    directory = settings.REVIEWS_PATH.format(year=year)
    for index in range(1, _get_count(directory)):
        path = os.path.join(directory, 'reviews.{}.json'.format(index))
        debug(path)
        with open(path, 'r') as file:
            if reviews is None:
                reviews = list()
            reviews += json.load(file)
    return reviews


def _stat_review(review):
    info('  Status      {}'.format('Closed' if review['closed'] else 'Open'))
    info('  Created On  {}'.format(review['created']))
    info('  # Reviewers {}'.format(len(review['reviewers'])))
    info('  # Messages  {}'.format(len(review['messages'])))
    info('  # Patchsets {}'.format(len(review['patchsets'])))


def _stat_reviews(reviews):
    info('  # Reviews     {}'.format(len(reviews)))
    open = set([review['issue'] for review in reviews if not review['closed']])
    info('  # Open        {}'.format(len(open)))

    messages = dict()
    comments = dict()
    patchsets = dict()
    for review in reviews:
        id = review['issue']

        messages[id] = len(review['messages'])
        patchsets[id] = len(review['patchsets'])
        comments[id] = 0
        for _, patchset in review['patchsets'].items():
            comments[id] += patchset['num_comments']

    info('  Top 10 # Messages')
    sorted_messages = sorted(
            messages.items(), key=operator.itemgetter(1), reverse=True
        )
    for (key, value) in sorted_messages[:10]:
        info('     {:<10} {}'.format(key, value))
    info('  Top 10 # Comments')
    sorted_comments = sorted(
            comments.items(), key=operator.itemgetter(1), reverse=True
        )
    for (key, value) in sorted_comments[:10]:
        info('     {:<10} {}'.format(key, value))
    info('  Top 10 # Patchsets')
    sorted_patchsets = sorted(
            patchsets.items(), key=operator.itemgetter(1), reverse=True
        )
    for (key, value) in sorted_patchsets[:10]:
        info('     {:<10} {}'.format(key, value))


def _validate(id, year):
    is_valid = False
    path = os.path.join(settings.IDS_PATH, '{}.csv'.format(year))
    with open(path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if int(row[0]) == id:
                is_valid = True
                break
    return is_valid


class Command(BaseCommand):
    help = 'Display statistics about single code review (if a code review ' \
           'identifier is specified) or all code reviews created in a ' \
           'specified year.'

    def add_arguments(self, parser):
        parser.add_argument(
                '-id', type=int, default=None, help='Code review identifier '
                'of a code review. When specified, statistics of the '
                'particular code review are displayed.'
            )
        parser.add_argument(
                'year', type=int, help='Retrict the computation of statistics '
                'to code reviews that were created in the specified year.'
            )

    def handle(self, *args, **options):
        id = options.get('id', None)
        year = options['year']

        begin = dt.now()
        try:
            if id is not None:
                if not _validate(id, year):
                    message = 'Code review with id {} was not created in ' \
                              'year {}'.format(id, year)
                    raise CommandError(message)
                review = _get_review(id, year)
                if review is None:
                    message = 'Code review with id {} was not found in the ' \
                              'set of code reviews retrieved.'.format(id, year)
                    raise CommandError(message)
                info('{}'.format(id))
                _stat_review(review)
            else:
                reviews = _get_reviews(year)
                info('{}'.format(year))
                _stat_reviews(reviews)
        except KeyboardInterrupt:
            warning('Attempting to abort.')
        finally:
            info('Time: {:.2f} mins'.format(get_elapsed(begin, dt.now())))
