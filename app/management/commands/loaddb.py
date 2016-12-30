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
BUG_ID_PATTERN = 'BUG=((?:\d+)(?:,\d+)*)'
BUG_ID_RE = re.compile(BUG_ID_PATTERN)


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
                (count, missing) = self.map_reviews_to_bugs(year)
                info('Created {} mappings'.format(count))
                warning('{} bugs were not found'.format(missing))
        except KeyboardInterrupt:
            warning('Attempting to abort.')
        finally:
            info('Time: {:.2f} mins'.format(get_elapsed(begin, dt.now())))

    def load_reviews(self, year):
        files = Files(settings)
        reviews = files.get_reviews(year)
        objects = list()
        for review in reviews:
            r = Review()

            r.id = review['issue']
            r.created = review['created']
            r.is_open = True if not review['closed'] else False
            r.num_messages = len(review['messages'])
            r.document = files.transform_review(review)

            objects.append(r)

            if (len(objects) % settings.DATABASES['default']['BULK']) == 0:
                Review.objects.bulk_create(objects)
                objects.clear()

        if len(objects) > 0:
            Review.objects.bulk_create(objects)

        return len(reviews)

    def load_bugs(self, year):
        files = Files(settings)
        bugs = files.get_bugs(year)
        for bug in bugs:
            b = Bug()

            b.id = bug['id']
            b.type = bug['type']
            b.status = bug['status']
            b.opened = dt.strptime(bug['opened'], '%b %d, %Y %H:%M:%S')
            b.document = bug
            if bug['cve'] != '':
                b.vulnerability_set.add(
                        *self._get_vulnerabilities(bug['cve'].split(',')),
                        bulk=False
                    )

            b.save()

        return len(bugs)

    def map_reviews_to_bugs(self, year):
        count = 0
        missing = 0
        reviews = Review.objects.filter(created__year=year)
        reviews = reviews.extra(
                where=["document ->> 'description' ~ %s"],
                params=[BUG_ID_PATTERN]
            )
        objects = list()
        for review in reviews:
            match = BUG_ID_RE.search(review.document['description'])
            for id in match.group(1).split(','):
                bug = get_row(Bug, id=id)
                if bug is not None:
                    objects.append(ReviewBug(review=review, bug=bug))
                    count += 1
                else:
                    missing += 1

            if (len(objects) % settings.DATABASES['default']['BULK']) == 0:
                ReviewBug.objects.bulk_create(objects)
                objects.clear()

        if len(objects) > 0:
            ReviewBug.objects.bulk_create(objects)

        return (count, missing)

    def _get_vulnerabilities(self, cves):
        vulnerabilities = list()
        for cve in cves:
            vulnerability = Vulnerability(cve='CVE-{}'.format(cve.strip()))
            vulnerabilities.append(vulnerability)
        return vulnerabilities
