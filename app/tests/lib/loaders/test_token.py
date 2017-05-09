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
                        'frederic.jacob.78', 'NN', 'B-NP'
                    ),
                    (2, '@', '@', '@', 'NNP', 'I-NP'),
                    (3, 'gmail.com', 'gmail.com', 'gmail.com', 'NN', 'I-NP'),
                    (4, 'changed', 'chang', 'change', 'VBD', 'B-VP'),
                    (5, 'reviewers', 'review', 'reviewer', 'NNS', 'B-NP'),
                    (6, ':', ':', ':', ':', 'O')
                ],
                '+ dgozman@chromium.org, pkasting@google.com': [
                    (1, '+', '+', '+', 'JJ', 'B-NP'),
                    (2, 'dgozman', 'dgozman', 'dgozman', 'NN', 'I-NP'),
                    (3, '@', '@', '@', 'NNP', 'I-NP'),
                    (
                        4, 'chromium.org', 'chromium.org', 'chromium.org',
                        'NN', 'I-NP'
                    ),
                    (5, ',', ',', ',', ',', 'O'),
                    (6, 'pkasting', 'pkast', 'pkasting', 'VBG', 'O'),
                    (7, '@', '@', '@', 'CD', 'B-NP'),
                    (8, 'google.com', 'google.com', 'google.com', 'NN', 'I-NP')
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
                        'position', 'token', 'stem', 'lemma', 'pos', 'chunk'
                    )
                )
        self.assertEqual(expected, actual, msg='Data:Token')
