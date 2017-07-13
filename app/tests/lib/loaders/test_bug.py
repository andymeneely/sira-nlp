from django import test
from django.conf import settings

from app.lib import loaders
from app.models import *


class BugLoaderTestCase(test.TestCase):
    def setUp(self):
        self.loader = loaders.BugLoader(settings, num_processes=2)

    def test_load(self):
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
                    628110, 628496, 636539, 613918, 619379, 626102, 642598
                ]
            )

        actual = self.loader.load()
        self.assertEqual(len(expected), actual, msg='Return')

        actual = list(Bug.objects.all().values_list('id', flat=True))
        self.assertCountEqual(expected, actual, msg='Data: Bug')

        # Bug Type
        expected = (
                [   # 2012
                    (138542, 'Bug')
                ] +
                [   # 2015
                    (492263, 'Bug-Security'), (460986, 'Bug'), (517548, 'Bug'),
                    (514551, 'Bug-Regression'), (514246, 'Bug-Regression'),
                    (545318, 'Launch-OWP'), (542060, 'Bug-Security'),
                    (528486, 'Bug'), (534718, 'Bug'), (522049, 'Bug'),
                    (521057, 'Bug'), (521826, 'Bug'), (522587, 'Bug'),
                    (522791, 'Bug-Security')
                ] +
                [   # 2016
                    (620126, 'Bug'), (613918, 'Bug-Security'),
                    (619379, 'Bug-Security'), (617492, 'Bug'),
                    (624894, 'Feature'), (626102, 'Bug'), (627655, 'Bug'),
                    (628110, 'Bug'), (625357, 'Bug'), (636539, 'Bug'),
                    (576270, 'Bug'), (610176, 'Bug'), (609260, 'Bug-Security'),
                    (613160, 'Bug-Security'), (602509, 'Bug'), (606056, 'Bug'),
                    (607690, 'Bug'), (583485, 'Bug'), (584783, 'Bug'),
                    (642598, 'Bug'), (628496, 'Bug')
                ]
            )

        actual = list(Bug.objects.all().values_list('id', 'type'))
        self.assertCountEqual(expected, actual, msg='Data: Bug Type')

        # Vulnerabilities
        expected = (
                [   # 2015
                    ('CVE-2015-1294', 'monorail'),
                    ('CVE-2015-1292', 'monorail'),
                ] +
                [   # 2016
                    ('CVE-2016-1681', 'monorail'),
                    ('CVE-2016-1702', 'monorail'),
                    ('CVE-2016-5167', 'monorail')
                ]
            )

        actual = list(Vulnerability.objects.values_list('id', 'source'))
        self.assertCountEqual(expected, actual, msg='Data: Vulnerability')

        # Vulnerability to Bug Mapping
        expected = (
                [   # 2015
                    ('CVE-2015-1294', 492263),
                    ('CVE-2015-1292', 522791),
                ] +
                [   # 2016
                    ('CVE-2016-1681', 613160),
                    ('CVE-2016-1702', 609260),
                    ('CVE-2016-5167', 613918),
                    ('CVE-2016-5167', 619379),
                    ('CVE-2016-5167', 642598)
                ]
            )
        actual = list(VulnerabilityBug.objects.values_list(
                'vulnerability_id', 'bug_id'
            ))
        self.assertCountEqual(expected, actual, msg='Data: VulnerabilityBug')
