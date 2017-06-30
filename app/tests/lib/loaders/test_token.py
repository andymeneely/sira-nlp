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
        loader = loaders.SentenceMessageLoader(
                settings, num_processes=2, review_ids=[1259853004]
            )
        _ = loader.load()
        loader = loaders.CommentLoader(
                settings, num_processes=2, review_ids=[1259853004]
            )
        _ = loader.load()
        loader = loaders.SentenceCommentLoader(
                settings, num_processes=2, review_ids=[1259853004]
            )
        _ = loader.load()

    def setUp(self):
        self.loader = loaders.TokenLoader(
                settings, num_processes=2, review_ids=[1259853004]
            )

    def test_load(self):
        # Sub-Test 1
        expected = {
                "There's no real win from doing so (we save one conditional in "
                "one place but have to add code to set the pref elsewhere) and "
                "it would make subsequent non-kiosk runs still disable the dev "
                "tools unless we added even more code to distinguish why the pr"
                "ef was originally set and then unset it.": [
                    (1, 'There', 'there', 'there', 'EX', 'B-NP'),
                    (2, "'s", "'s", "'s", 'VBZ', 'B-VP'),
                    (3, 'no', 'no', 'no', 'DT', 'B-NP'),
                    (4, 'real', 'real', 'real', 'JJ', 'I-NP'),
                    (5, 'win', 'win', 'win', 'NN', 'I-NP'),
                    (6, 'from', 'from', 'from', 'IN', 'B-PP'),
                    (7, 'doing', 'do', 'do', 'VBG', 'B-VP'),
                    (8, 'so', 'so', 'so', 'RB', 'I-VP'),
                    (9, '(', '(', '(', '(', 'O'),
                    (10, 'we', 'we', 'we', 'PRP', 'B-NP'),
                    (11, 'save', 'save', 'save', 'VBP', 'B-VP'),
                    (12, 'one', 'one', 'one', 'CD', 'B-NP'),
                    (13, 'conditional', 'condit', 'conditional', 'NN', 'I-NP'),
                    (14, 'in', 'in', 'in', 'IN', 'B-PP'),
                    (15, 'one', 'one', 'one', 'CD', 'B-NP'),
                    (16, 'place', 'place', 'place', 'NN', 'I-NP'),
                    (17, 'but', 'but', 'but', 'CC', 'O'),
                    (18, 'have', 'have', 'have', 'VBP', 'B-VP'),
                    (19, 'to', 'to', 'to', 'TO', 'I-VP'),
                    (20, 'add', 'add', 'add', 'VB', 'I-VP'),
                    (21, 'code', 'code', 'code', 'NN', 'B-NP'),
                    (22, 'to', 'to', 'to', 'TO', 'B-VP'),
                    (23, 'set', 'set', 'set', 'VB', 'I-VP'),
                    (24, 'the', 'the', 'the', 'DT', 'B-NP'),
                    (25, 'pref', 'pref', 'pref', 'NN', 'I-NP'),
                    (26, 'elsewhere', 'elsewher', 'elsewhere', 'RB', 'O'),
                    (27, ')', ')', ')', ')', 'O'),
                    (28, 'and', 'and', 'and', 'CC', 'O'),
                    (29, 'it', 'it', 'it', 'PRP', 'B-NP'),
                    (30, 'would', 'would', 'would', 'MD', 'B-VP'),
                    (31, 'make', 'make', 'make', 'VB', 'I-VP'),
                    (32, 'subsequent', 'subsequ', 'subsequent', 'JJ', 'B-NP'),
                    (33, 'non-kiosk', 'non-kiosk', 'non-kiosk', 'NN', 'I-NP'),
                    (34, 'runs', 'run', 'run', 'NNS', 'I-NP'),
                    (35, 'still', 'still', 'still', 'RB', 'O'),
                    (36, 'disable', 'disabl', 'disable', 'VB', 'O'),
                    (37, 'the', 'the', 'the', 'DT', 'B-NP'),
                    (38, 'dev', 'dev', 'dev', 'NN', 'I-NP'),
                    (39, 'tools', 'tool', 'tool', 'VBZ', 'B-VP'),
                    (40, 'unless', 'unless', 'unless', 'IN', 'B-PP'),
                    (41, 'we', 'we', 'we', 'PRP', 'B-NP'),
                    (42, 'added', 'ad', 'add', 'VBD', 'B-VP'),
                    (43, 'even', 'even', 'even', 'RB', 'I-VP'),
                    (44, 'more', 'more', 'more', 'RBR', 'O'),
                    (45, 'code', 'code', 'code', 'NN', 'B-NP'),
                    (46, 'to', 'to', 'to', 'TO', 'B-VP'),
                    (
                        47, 'distinguish', 'distinguish', 'distinguish', 'VB',
                       'I-VP'
                    ),
                    (48, 'why', 'whi', 'why', 'WRB', 'O'),
                    (49, 'the', 'the', 'the', 'DT', 'B-NP'),
                    (50, 'pref', 'pref', 'pref', 'NN', 'I-NP'),
                    (51, 'was', 'wa', 'be', 'VBD', 'B-VP'),
                    (52, 'originally', 'origin', 'originally', 'RB', 'I-VP'),
                    (53, 'set', 'set', 'set', 'VBN', 'I-VP'),
                    (54, 'and', 'and', 'and', 'CC', 'I-VP'),
                    (55, 'then', 'then', 'then', 'RB', 'O'),
                    (56, 'unset', 'unset', 'unset', 'VB', 'O'),
                    (57, 'it', 'it', 'it', 'PRP', 'B-NP'),
                    (58, '.', '.', '.', '.', 'O')
                ],
                'I would not try to set that pref in kiosk mode.': [
                    (1, 'I', 'i', 'i', 'PRP', 'B-NP'),
                    (2, 'would', 'would', 'would', 'MD', 'B-VP'),
                    (3, 'not', 'not', 'not', 'RB', 'I-VP'),
                    (4, 'try', 'tri', 'try', 'VB', 'I-VP'),
                    (5, 'to', 'to', 'to', 'TO', 'I-VP'),
                    (6, 'set', 'set', 'set', 'VB', 'I-VP'),
                    (7, 'that', 'that', 'that', 'DT', 'B-NP'),
                    (8, 'pref', 'pref', 'pref', 'NN', 'I-NP'),
                    (9, 'in', 'in', 'in', 'IN', 'B-PP'),
                    (10, 'kiosk', 'kiosk', 'kiosk', 'JJ', 'B-NP'),
                    (11, 'mode', 'mode', 'mode', 'NN', 'I-NP'),
                    (12, '.', '.', '.', '.', 'O')
                ]
            }
        _ = self.loader.load()

        actual = dict()
        message = Message.objects.get(
                review__id=1259853004, posted='2015-07-30 23:55:34.517080'
            )
        for sentence in message.sentences.all():
            actual[sentence.text] = list(
                    Token.objects.filter(sentence=sentence)
                    .order_by('position')
                    .values_list(
                        'position', 'token', 'stem', 'lemma', 'pos', 'chunk'
                    )
                )

        self.assertEqual(expected, actual, msg='Data:Token')


        # Sub-Test 2
        expected = {
                "You can probably nuke the comment on that since it's just rest"
                "ating the code, rather than trying to expand it.": [
                    (1, 'You', 'you', 'you', 'PRP', 'B-NP'),
                    (2, 'can', 'can', 'can', 'MD', 'B-VP'),
                    (3, 'probably', 'probabl', 'probably', 'RB', 'I-VP'),
                    (4, 'nuke', 'nuke', 'nuke', 'VB', 'I-VP'),
                    (5, 'the', 'the', 'the', 'DT', 'B-NP'),
                    (6, 'comment', 'comment', 'comment', 'NN', 'I-NP'),
                    (7, 'on', 'on', 'on', 'IN', 'B-PP'),
                    (8, 'that', 'that', 'that', 'DT', 'B-NP'),
                    (9, 'since', 'sinc', 'since', 'IN', 'B-PP'),
                    (10, 'it', 'it', 'it', 'PRP', 'B-NP'),
                    (11, "'s", "'s", "'s", 'VBZ', 'B-VP'),
                    (12, 'just', 'just', 'just', 'RB', 'I-VP'),
                    (13, 'restating', 'restat', 'restate', 'VBG', 'I-VP'),
                    (14, 'the', 'the', 'the', 'DT', 'B-NP'),
                    (15, 'code', 'code', 'code', 'NN', 'I-NP'),
                    (16, ',', ',', ',', ',', 'O'),
                    (17, 'rather', 'rather', 'rather', 'RB', 'O'),
                    (18, 'than', 'than', 'than', 'IN', 'O'),
                    (19, 'trying', 'tri', 'try', 'VBG', 'O'),
                    (20, 'to', 'to', 'to', 'TO', 'O'),
                    (21, 'expand', 'expand', 'expand', 'VB', 'O'),
                    (22, 'it', 'it', 'it', 'PRP', 'B-NP'),
                    (23, '.', '.', '.', '.', 'O')
                ],
                'Nit: Just combine this conditional with the one below.': [
                    (1, 'Nit', 'nit', 'nit', 'NN', 'B-NP'),
                    (2, ':', ':', ':', ':', 'O'),
                    (3, 'Just', 'just', 'just', 'RB', 'O'),
                    (4, 'combine', 'combin', 'combine', 'VB', 'O'),
                    (5, 'this', 'thi', 'this', 'DT', 'B-NP'),
                    (6, 'conditional', 'condit', 'conditional', 'JJ', 'I-NP'),
                    (7, 'with', 'with', 'with', 'IN', 'B-PP'),
                    (8, 'the', 'the', 'the', 'DT', 'B-NP'),
                    (9, 'one', 'one', 'one', 'CD', 'I-NP'),
                    (10, 'below', 'below', 'below', 'NN', 'I-NP'),
                    (11, '.', '.', '.', '.', 'O')
                ]
            }
        comment = Comment.objects.get(
                patch__patchset__review_id=1259853004,
                posted='2015-07-30 18:24:22.286210'
            )
        actual = dict()
        for sentence in comment.sentences.iterator():
            actual[sentence.text] = list(
                    Token.objects.filter(sentence=sentence)
                    .order_by('position')
                    .values_list(
                        'position', 'token', 'stem', 'lemma', 'pos', 'chunk'
                    )
                )

        self.assertEqual(expected, actual, msg='Data:Token')
