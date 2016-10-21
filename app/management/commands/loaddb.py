import ast
import os

from datetime import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from app.lib.files import *
from app.lib.helpers import *
from app.lib.logger import *
from app.lib.rietveld import *
from app.models import *

# Match the bug ID(s) in the code review description
BUG_ID_RE = re.compile('BUG=((?:\d+)(?:,\d+)*)')


class Command(BaseCommand):
    help = 'Load the database with code review and bug information.'

    def add_arguments(self, parser):
        parser.add_argument(
                'year', type=int, help='Load only those code reviews that '
                'were created in the specified year.'
            )

    def handle(self, *args, **options):
        year = options['year']

        begin = dt.now()
        try:
            with transaction.atomic():
                info('Loading bugs for the year {}'.format(year))
                count = self.load_bugs(year)
                info('Loaded {} bugs'.format(count))
                info('Loading reviews for the year {}'.format(year))
                count = self.load_reviews(year)
                info('Loaded {} reviews'.format(count))
                info('Mapping reviews to bugs')
                count = self.map_reviews_to_bugs(year)
                info('Created {} mappings'.format(count))
        except KeyboardInterrupt:
            warning('Attempting to abort.')
        finally:
            info('Time: {:.2f} mins'.format(get_elapsed(begin, dt.now())))

    def load_reviews(self, year):
        files = Files(settings)
        reviews = files.get_reviews(year)
        _reviews = list()
        for (index, review) in enumerate(reviews):
            _review = Review()

            _review.id = review['issue']
            _review.created = review['created']
            _review.is_open = True if not review['closed'] else False
            # TODO: Remove hardcoding once success criteria is defined
            _review.is_successful = True
            if BUG_ID_RE.search(review['description']) is not None:
                _review.has_bug = True
            _review.num_messages = len(review['messages'])
            _review.document = review

            _reviews.append(_review)
            if (index % settings.DATABASES['default']['BULK']) == 0:
                Review.objects.bulk_create(_reviews)
                _reviews.clear()

        if len(_reviews) > 0:
            Review.objects.bulk_create(_reviews)

        return (index + 1)

    def load_bugs(self, year):
        files = Files(settings)
        bugs = files.get_bugs(year)
        for (index, bug) in enumerate(bugs):
            _vulnerabilities = None
            _bug = Bug()

            _bug.id = bug['id']
            _bug.type = bug['type']
            _bug.status = bug['status']
            _bug.opened = dt.strptime(bug['opened'], '%b %d, %Y %H:%M:%S')
            if bug['cve'] != '':
                _vulnerabilities = [
                        Vulnerability(id='CVE-{}'.format(cve.strip()))
                        for cve in bug['cve'].split(',')
                    ]
            else:
                _vulnerabilites = [
                        Vulnerability(id=label)
                        for label in bug['labels'].split(',')
                        if 'CVE-' in label
                    ]
            _bug.document = bug
            _bug.save()

            if _vulnerabilities is not None:
                for _vulnerability in _vulnerabilities:
                    _vulnerability.bug = _bug
                    _vulnerability.save()

        return (index + 1)

    def map_reviews_to_bugs(self, year):
        count = 0
        mappings = list()
        reviews = Review.objects.filter(created__year=year, has_bug=True)
        for review in reviews:
            match = BUG_ID_RE.search(review.document['description'])
            if match:
                for id in match.group(1).split(','):
                    bug = get_row(Bug, id=id)
                    if bug is not None:
                        mappings.append(ReviewBug(review=review, bug=bug))
                        count += 1

            if (len(mappings) % settings.DATABASES['default']['BULK']) == 0:
                ReviewBug.objects.bulk_create(mappings)
                mappings.clear()

        if len(mappings) > 0:
            ReviewBug.objects.bulk_create(mappings)

        return count
