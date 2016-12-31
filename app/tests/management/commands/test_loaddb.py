import os

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils.six import StringIO

from app.models import *

DATA_PATH = os.path.join(settings.BASE_DIR, 'app/tests/data')


@override_settings(
    IDS_PATH=os.path.join(DATA_PATH, 'ids'),
    BUGS_PATH=os.path.join(DATA_PATH, 'bugs/{year}'),
    REVIEWS_PATH=os.path.join(DATA_PATH, 'reviews/{year}')
)
class LoaddbTestCase(TestCase):
    def setUp(self):
        pass

    @override_settings(YEARS=[2015])
    def test_handle_year_2015(self):
        call_command('loaddb')

        # Reviews
        expected = [
                1286193008, 1293023003, 1295003003, 1295403003, 1299243002,
                1304613003, 1321103002, 1318783003, 1188433011, 1308723003
            ]
        actual = list(Review.objects.values_list('id', flat=True))
        self.assertCountEqual(expected, actual)

        review = Review.objects.get(id=1308723003)
        self.assertTrue('reviewed_files' in review.document)
        self.assertTrue('committed_files' in review.document)

        # Bugs
        expected = [
                517548, 522587, 522049, 460986, 514246, 521826, 492263, 522791,
                534718, 545318
            ]
        actual = list(Bug.objects.values_list('id', flat=True))
        self.assertCountEqual(expected, actual)

        # Review to Bug Mappings
        expected = [
                (1286193008, 517548), (1293023003, 522587),
                (1295003003, 522049), (1295403003, 460986),
                (1299243002, 514246), (1304613003, 521826),
                (1188433011, 492263), (1308723003, 522791)
            ]
        actual = list(ReviewBug.objects.values_list('review_id', 'bug_id'))
        self.assertCountEqual(expected, actual)

        # Vulnerabilities
        expected = [
                ('CVE-2015-1294', 492263, 'monorail'),
                ('CVE-2015-1292', 522791, 'monorail')
            ]
        actual = list(
                Vulnerability.objects.values_list('cve', 'bug_id', 'source')
            )
        self.assertCountEqual(expected, actual)

    @override_settings(YEARS=[2016])
    def test_handle_year_2016(self):
        call_command('loaddb')

        # Reviews
        expected = [
                1999153002, 2027643002, 2140383005, 2148643002, 2148653002,
                2148793002, 2149523002, 2150783003, 2151613002, 2151763003,
                2050053002, 2048483002
            ]
        actual = list(Review.objects.values_list('id', flat=True))
        self.assertCountEqual(expected, actual)

        review = Review.objects.get(id=1999153002)
        self.assertTrue('reviewed_files' in review.document)
        self.assertTrue('committed_files' in review.document)

        # Bugs
        expected = [
                606056, 610176, 627655, 602509, 584783, 628496, 624894, 617492,
                609260, 613160, 625357, 628110
            ]
        actual = list(Bug.objects.values_list('id', flat=True))
        self.assertCountEqual(expected, actual)

        # Review to Bug Mapping
        expected = [
                (1999153002, 613160), (2027643002, 609260),
                (2140383005, 606056), (2148643002, 627655),
                (2148653002, 602509), (2148793002, 584783),
                (2149523002, 628496), (2150783003, 617492),
                (2151613002, 625357), (2151763003, 628110)
            ]
        actual = list(ReviewBug.objects.values_list('review_id', 'bug_id'))
        self.assertCountEqual(expected, actual)

        # Vulnerabilities
        expected = [
                ('CVE-2016-1681', 613160, 'monorail'),
                ('CVE-2016-1702', 609260, 'monorail')
            ]
        actual = list(
                Vulnerability.objects.values_list('cve', 'bug_id', 'source')
            )
        self.assertCountEqual(expected, actual)

    @override_settings(YEARS=[2015, 2016])
    def test_handle_issue_4(self):
        '''Test fix for issue #4

        See https://github.com/andymeneely/sira-nlp/issues/4 for more
        information.
        '''
        call_command('loaddb')

        self.assertEqual(22, Review.objects.all().count())
        self.assertEqual(22, Bug.objects.all().count())
        self.assertEqual(20, ReviewBug.objects.all().count())
        self.assertEqual(4, Vulnerability.objects.all().count())

        self.assertTrue(
                ReviewBug.objects.filter(
                    review__id=2050053002, bug__id=534718
                ).exists()
            )
        self.assertTrue(
                ReviewBug.objects.filter(
                    review__id=2048483002, bug__id=545318
                ).exists()
            )
