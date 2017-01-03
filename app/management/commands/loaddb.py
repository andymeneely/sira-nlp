import os

from datetime import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from app.lib.files import *
from app.lib.helpers import *
from app.lib.logger import *
from app.models import *

# Match the bug ID(s) in the code review description
BUG_ID_PATTERN = 'BUG=((?:\d+)(?:,\d+)*)'
BUG_ID_RE = re.compile(BUG_ID_PATTERN)


class Command(BaseCommand):
    help = 'Load the database with code review and bug information.'

    def handle(self, *args, **options):
        begin = dt.now()
        try:
            with transaction.atomic():
                info('Bugs')
                for year in settings.YEARS:
                    count = self.load_bugs(year)
                    info('  {}: {}'.format(year, count))
                info('Vulnerabilities')
                count = self.load_vulnerabilities()
                info('  {}'.format(count))
                info('Reviews')
                for year in settings.YEARS:
                    count = self.load_reviews(year)
                    info('  {}: {}'.format(year, count))
                info('Bug to Review Mapping')
                for year in settings.YEARS:
                    (count, missing) = self.map_reviews_to_bugs(year)
                    info('  {}: {}'.format(year, count))
                    if missing > 0:
                        warning('  {}: {} missing'.format(year, missing))
        except KeyboardInterrupt:
            warning('Attempting to abort.')
        finally:
            info('Time: {:.2f} mins'.format(get_elapsed(begin, dt.now())))

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

    def load_vulnerabilities(self):
        files = Files(settings)
        vulnerabilities = files.get_vulnerabilities()
        for (source, cve, bug_id) in vulnerabilities:
            b = helpers.get_row(Bug, id=bug_id)
            if b is None:
                b = Bug(id=bug_id, type='Bug-Security', status='Redacted')
                b.save()
            v = Vulnerability(cve=cve, source=source, bug=b)
            v.save()

        return len(vulnerabilities)

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
