import os

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase
from django.utils.six import StringIO

from app.models import *


class TestLoaddbCommand(TestCase):
    def setUp(self):
        pass

    def test_handle(self):
        data_path = os.path.join(settings.BASE_DIR, 'app/tests/data')
        with self.settings(
                IDS_PATH=os.path.join(data_path, 'ids'),
                BUGS_PATH=os.path.join(data_path, 'bugs/{year}'),
                REVIEWS_PATH=os.path.join(data_path, 'reviews/{year}')
             ):

            call_command('loaddb', '2016')

            self.assertEqual(10, Review.objects.all().count())
            self.assertEqual(10, Bug.objects.all().count())
            self.assertEqual(8, ReviewBug.objects.all().count())
            self.assertEqual(2, Vulnerability.objects.all().count())

            self.assertTrue(
                    ReviewBug.objects.filter(
                        review__id=2148643002, bug__id=627655
                    ).exists()
                )
            self.assertTrue(
                    ReviewBug.objects.filter(
                        review__id=2148653002, bug__id=602509
                    ).exists()
                )
            self.assertTrue(
                    Vulnerability.objects.filter(
                        cve='CVE-2016-1681', bug__id=613160
                    )
                )
            self.assertTrue(
                    Vulnerability.objects.filter(
                        cve='CVE-2016-1702', bug__id=609260
                    )
                )

            self.assertTrue(
                    'reviewed_files' in
                    (Review.objects.get(id=1999153002)).document
                )
            self.assertTrue(
                    'committed_files' in
                    (Review.objects.get(id=1999153002)).document
                )
