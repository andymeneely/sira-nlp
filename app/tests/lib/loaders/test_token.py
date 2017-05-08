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
        loader = loaders.SentenceLoader(
                settings, num_processes=2, review_ids=[1259853004]
            )
        _ = loader.load()

    def setUp(self):
        self.loader = loaders.TokenLoader(
                settings, num_processes=2, review_ids=[1259853004]
            )

    def test_load(self):
        expected = {
                'frederic.jacob.78@gmail.com changed reviewers:': [
                    (
                        1, 'frederic.jacob.78', 'frederic.jacob.78',
                        'frederic.jacob.78', 'NN'
                    ),
                    (2, '@', '@', '@', 'NNP'),
                    (3, 'gmail.com', 'gmail.com', 'gmail.com', 'NN'),
                    (4, 'changed', 'chang', 'change', 'VBD'),
                    (5, 'reviewers', 'review', 'reviewer', 'NNS'),
                    (6, ':', ':', ':', ':')
                ],
                '+ dgozman@chromium.org, pkasting@google.com': [
                    (1, '+', '+', '+', 'JJ'),
                    (2, 'dgozman', 'dgozman', 'dgozman', 'NN'),
                    (3, '@', '@', '@', 'NNP'),
                    (4, 'chromium.org', 'chromium.org', 'chromium.org', 'NN'),
                    (5, ',', ',', ',', ','),
                    (6, 'pkasting', 'pkast', 'pkasting', 'VBG'),
                    (7, '@', '@', '@', 'CD'),
                    (8, 'google.com', 'google.com', 'google.com', 'NN')
                ]
            }

        _ = self.loader.load()

        actual = dict()
        sentences = Sentence.objects.filter(
                review_id=1259853004,
                message__posted='2015-07-30 10:32:31.936180'
            )
        for sentence in sentences:
            actual[sentence.text] = list(
                    Token.objects.filter(sentence=sentence)
                    .order_by('position')
                    .values_list(
                        'position', 'token', 'stem', 'lemma', 'pos'
                    )
                )
        self.assertEqual(expected, actual, msg='Data:Token')
