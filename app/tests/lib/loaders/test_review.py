from django import test
from django.conf import settings

from app.lib import loaders
from app.models import *


class BugLoaderTestCase(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        loader = loaders.BugLoader(settings)
        _ = loader.load()

    def setUp(self):
        self.loader = loaders.ReviewLoader(settings)

    def test_load(self):
        # Vulnerabilities
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

        actual = self.loader.load()
        self.assertEqual(len(expected), actual, msg='Return')

        actual = list(Review.objects.all().values_list('id', flat=True))
        self.assertCountEqual(expected, actual, msg='Data:Review')

        # Review to Bug Mappings
        expected = (
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
                    (2151763003, 628110), (2210603002, 607690),
                    (2230993004, 636539)
                ] +
                [   # Review from 2016 and Bug from 2015
                    (2050053002, 534718), (2048483002, 545318),
                    (2211423003, 528486)
                ]
            )
        actual = list(ReviewBug.objects.values_list('review_id', 'bug_id'))
        self.assertCountEqual(expected, actual)
