import os

from django.conf import settings
from django.core.management import call_command
from django.db import transaction
from django.test import TestCase, override_settings
from django.utils.six import StringIO

from app.models import *

DATA_PATH = os.path.join(settings.BASE_DIR, 'app/tests/data')


@override_settings(
    IDS_PATH=os.path.join(DATA_PATH, 'ids'),
    BUGS_PATH=os.path.join(DATA_PATH, 'bugs/{year}'),
    REVIEWS_PATH=os.path.join(DATA_PATH, 'reviews/{year}'),
    VULNERABILITIES_PATH=os.path.join(DATA_PATH, 'vulnerabilities')
)
class LoaddbTestCase(TestCase):
    def setUp(self):
        pass

    def test_handle(self):
        call_command('loaddb')

        # Reviews
        expected = (
                [   # 2013
                    12314009
                ] +
                [   # 2015
                    1128633002, 1144393004, 1188433011, 1247623005, 1259853004,
                    1286193008, 1292403004, 1293023003, 1295003003, 1295403003,
                    1299243002, 1304613003, 1308723003, 1318783003, 1321103002,
                    1444413002, 1454003003, 1457243002, 1544273002
                ] +
                [   # 2016
                    1999153002, 2027643002, 2140383005, 2148643002, 2148653002,
                    2148793002, 2149523002, 2150783003, 2151613002, 2151763003,
                    2050053002, 2048483002, 2177983004, 2134723002, 2085023003,
                    2256073002, 2230993004, 2211423003, 2223093002, 2210603002,
                    2189523002, 2168223002
                ]
            )
        actual = list(Review.objects.values_list('id', flat=True))
        self.assertCountEqual(expected, actual, msg='Reviews mismatch.')

        # Bugs
        expected = (
                [   # 2012
                    138542
                ] +
                [   # 2015
                    460986, 492263, 514246, 514551, 517548, 521057, 521826,
                    522049, 522587, 522791, 528486, 534718, 542060, 545318
                ] +
                [   # 2016
                    576270, 583485, 584783, 602509, 606056, 607690, 609260,
                    610176, 613160, 617492, 620126, 624894, 625357, 627655,
                    628110, 628496, 636539
                ] +
                [   # Manually Added (aka Redacted)
                    618037, 174059
                ]
            )
        actual = list(Bug.objects.values_list('id', flat=True))
        self.assertCountEqual(expected, actual, msg='Bugs mismatch.')

        expected = [
                (618037, 'Bug-Security', 'Redacted'),
                (174059, 'Bug-Security', 'Redacted')
            ]
        actual = list(
                Bug.objects
                .filter(id__in=[618037, 174059])
                .values_list('id', 'type', 'status')
            )
        self.assertCountEqual(expected, actual, msg='Redacted bugs mismatch.')

        # Review to Bug Mappings
        expected = (
                [   # 2013
                    (12314009, 174059)
                ] +
                [   # 2015
                    (1188433011, 492263), (1259853004, 514551),
                    (1286193008, 517548), (1292403004, 521057),
                    (1293023003, 522587), (1295003003, 522049),
                    (1295403003, 460986), (1299243002, 514246),
                    (1304613003, 521826), (1308723003, 522791),
                    (1454003003, 542060)
                ] +
                [   # Review from 2015 and Bug from 2012
                    (1544273002, 138542)
                ] +
                [   # 2016
                    (1999153002, 613160), (2027643002, 609260),
                    (2085023003, 583485), (2134723002, 576270),
                    (2134723002, 620126), (2140383005, 606056),
                    (2148643002, 627655), (2148653002, 602509),
                    (2148793002, 584783), (2149523002, 628496),
                    (2150783003, 617492), (2151613002, 625357),
                    (2151763003, 628110), (2177983004, 618037),
                    (2210603002, 607690), (2223093002, 618037),
                    (2230993004, 636539)
                ] +
                [   # Review from 2016 and Bug from 2015
                    (2050053002, 534718), (2048483002, 545318),
                    (2211423003, 528486)
                ]
            )
        actual = list(ReviewBug.objects.values_list('review_id', 'bug_id'))
        self.assertCountEqual(expected, actual)

        # Vulnerabilities
        expected = (
                [   # 2015
                    ('CVE-2015-1294', 492263, 'monorail'),
                    ('CVE-2015-1292', 522791, 'monorail'),
                ] +
                [   # 2016
                    ('CVE-2016-1681', 613160, 'monorail'),
                    ('CVE-2016-1702', 609260, 'monorail')
                ] +
                [   # Manually Added
                    ('CVE-2016-5165', 618037, 'blog'),
                    ('CVE-2016-2845', 542060, 'manual'),
                    ('CVE-2013-0908', 174059, 'manual')
                ]
            )
        actual = list(
                Vulnerability.objects.values_list('cve', 'bug_id', 'source')
            )
        self.assertCountEqual(expected, actual)

        # Missed Vulnerability Reviews
        expected = [
                1128633002, 1144393004, 1247623005, 1259853004, 1292403004,
                1444413002, 1544273002, 2085023003, 2134723002, 2168223002,
                2177983004, 2189523002, 2210603002, 2211423003
            ]
        actual = list(
                Review.objects.filter(missed_vulnerability=True)
                .values_list('id', flat=True)
            )
        self.assertCountEqual(expected, actual)

    def test_handle_issue_4(self):
        '''Test fix for issue #4

        See https://github.com/andymeneely/sira-nlp/issues/4 for more
        information.
        '''
        with self.settings(YEARS=[2016]):
            call_command('loaddb')

            self.assertFalse(
                    ReviewBug.objects.filter(
                        review__id=2050053002, bug__id=534718
                    ).exists()
                )
            self.assertFalse(
                    ReviewBug.objects.filter(
                        review__id=2048483002, bug__id=545318
                    ).exists()
                )
            self.assertFalse(
                    ReviewBug.objects.filter(
                        review__id=2211423003, bug__id=528486
                    ).exists()
                )

            for model in [Vulnerability, ReviewBug, Review, Bug]:
                model.objects.all().delete()

        with self.settings(YEARS=[2015, 2016]):
            call_command('loaddb')

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
            self.assertTrue(
                    ReviewBug.objects.filter(
                        review__id=2211423003, bug__id=528486
                    ).exists()
                )
