from django import test
from django.conf import settings

from app.lib import loaders
from app.models import *


class TokenLoaderTestCase(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        loader = loaders.ReviewLoader(settings, num_processes=2)
        _ = loader.load()
        loader = loaders.MessageLoader(
                settings, num_processes=2, review_ids=[1259853004]
            )
        _ = loader.load()

    def setUp(self):
        self.loader = loaders.TokenLoader(
                settings, num_processes=2, review_ids=[1259853004]
            )

    def test_load(self):
        expected = [
                ('frederic.jacob.78', 'frederic.jacob.78', 1, 'NN'),
                ('@', '@', 2, 'NNP'),
                ('gmail.com', 'gmail.com', 1, 'NN'),
                ('changed', 'change', 1, 'VBD'),
                ('reviewers', 'reviewer', 1, 'NNS'),
                (':', ':', 1, ':'),
                ('+', '+', 1, 'JJ'),
                ('dgozman', 'dgozman', 1, 'NN'),
                ('chromium.org', 'chromium.org', 1, 'NN'),
                (',', ',', 1, ','),
                ('pkasting', 'pkasting', 1, 'VBG'),
                ('@', '@', 1, 'CD'),
                ('google.com', 'google.com', 1, 'NN')
            ]

        _ = self.loader.load()

        actual = list(
                Token.objects.filter(
                    message__review_id=1259853004,
                    message__posted='2015-07-30 10:32:31.936180'
                ).values_list('token', 'lemma', 'frequency', 'pos')
            )
        self.assertCountEqual(expected, actual, msg='Data:Token')
