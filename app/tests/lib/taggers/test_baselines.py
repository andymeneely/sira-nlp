from django import test
from django.conf import settings
from django.db import connections
from django.db.models import Q

from app.lib import loaders, taggers
from app.models import *

from django.core.management import call_command


class BaselinesTaggerTestCase(test.TransactionTestCase):
    def setUp(self):
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
        loader = loaders.TokenLoader(
                settings, num_processes=2, review_ids=[1259853004]
            )
        _ = loader.load()

        connections.close_all()  # Hack

        q1 = Q(message__review_id=1259853004)
        q2 = Q(comment__patch__patchset__review_id=1259853004)
        sentObjects = Sentence.objects.filter(q1 | q2)
        self.tagger = taggers.BaselinesTagger(
                settings, num_processes=2, sentenceObjects=sentObjects,
                metrics = [
                        'sent_length', 'type_token_ratio', 'pronoun_density',
                        'flesch_kincaid', 'stop_word_ratio', 'question_ratio',
                        'conceptual_similarity'
                    ]
            )

    def test_load(self):
        expected = [
                ('Code to disconnect the DevTools in kiosk mode.',
                 9, 1.0, 3.7,
                 {'1ST': 0.0, '3RD': 0.0, 'TOT': 0.0, '2ND': 0.0}
                ),
                ('Did you have any place in mind where we can set the policy?',
                 14, 1.0, 4.2,
                 {'1ST': 0.07142857142857142, '3RD': 0.0,
                  'TOT': 0.14285714285714285, '2ND': 0.07142857142857142}
                ),
                ("Don't you think that it could make it more difficult",
                 11, 0.9090909090909091, 2.6,
                 {'1ST': 0.0, '3RD': 0.18181818181818182,
                  'TOT': 0.2727272727272727, '2ND': 0.09090909090909091}
                ),
                ('Done.',
                 2, 1.0, -3.0,
                 {'1ST': 0.0, '3RD': 0.0, 'TOT': 0.0, '2ND': 0.0},
                ),
                ('Done.',
                 2, 1.0, -3.0,
                 {'1ST': 0.0, '3RD': 0.0, 'TOT': 0.0, '2ND': 0.0},
                ),
                ('I have put it there because it is the central place for the D'
                 'evtools creation and as such cover all possible case.',
                 23, 0.9130434782608695, 8.8,
                 {'1ST': 0.043478260869565216, '3RD': 0.08695652173913043,
                  'TOT': 0.13043478260869565, '2ND': 0.0}
                ),
                ('I looked all over the code and I did not saw any place that l'
                 'ooked good to set',
                 18, 0.8888888888888888, 4.5,
                 {'1ST': 0.1111111111111111, '3RD': 0.0,
                  'TOT': 0.1111111111111111, '2ND': 0.0}
                ),
                ('I removed the comment and merged the two conditions.',
                 10, 0.9, 4.8,
                 {'1ST': 0.1, '3RD': 0.0, 'TOT': 0.1, '2ND': 0.0}
                ),
                ('I though that it will fit in chrome/browser/prefs, but all th'
                 'e policies',
                 13, 1.0, 4.9,
                 {'1ST': 0.07692307692307693, '3RD': 0.07692307692307693,
                  'TOT': 0.15384615384615385, '2ND': 0.0}
                ),
                ('I would not try to set that pref in kiosk mode.',
                 12, 1.0, 1.9,
                 {'1ST': 0.08333333333333333, '3RD': 0.0,
                  'TOT': 0.08333333333333333, '2ND': 0.0}
                ),
                ('Is it possible to set the policy |prefs::kDevToolsDisabled| i'
                 'nstead in kiosk mode?',
                 15, 1.0, 6.8,
                 {'1ST': 0.0, '3RD': 0.06666666666666667,
                  'TOT': 0.06666666666666667, '2ND': 0.0}
                ),
                ('It work for all OS (Tested it on Win,Osx,Linux) and there are'
                 ' already code to disable the Devtools at this place.',
                 28, 0.9642857142857143, 9.7,
                 {'1ST': 0.0, '3RD': 0.07142857142857142,
                  'TOT': 0.07142857142857142, '2ND': 0.0}
                ),
                ('LGTM',
                 1, 1.0, -3.4,
                 {'1ST': 0.0, '3RD': 0.0, 'TOT': 0.0, '2ND': 0.0}
                ),
                ('Looks like you need LGTM from a devtools owner.',
                 10, 1.0, 1.3,
                 {'1ST': 0.0, '3RD': 0.0, 'TOT': 0.1, '2ND': 0.1}
                ),
                ('Nit: Just combine this conditional with the one below.',
                 11, 1.0, 5.9,
                 {'1ST': 0.0, '3RD': 0.0, 'TOT': 0.0, '2ND': 0.0}
                ),
                ('Nit: No blank line here',
                 6, 1.0, -1.4,
                 {'1ST': 0.0, '3RD': 0.0, 'TOT': 0.0, '2ND': 0.0}
                ),
                ("There's no real win from doing so (we save one conditional in"
                 " one place but have to add code to set the pref elsewhere) an"
                 "d it would make subsequent non-kiosk runs still disable the d"
                 "ev tools unless we added even more code to distinguish why th"
                 "e pref was originally set and then unset it.",
                 58, 0.8103448275862069, 22.9,
                 {'1ST': 0.034482758620689655, '3RD': 0.034482758620689655,
                  'TOT': 0.06896551724137931, '2ND': 0.0}
                ),
                ("You can probably nuke the comment on that since it's just res"
                 "tating the code, rather than trying to expand it.",
                 23, 0.9130434782608695, 9.3,
                 {'1ST': 0.0, '3RD': 0.08695652173913043,
                  'TOT': 0.13043478260869565, '2ND': 0.043478260869565216}
                ),
                ('are a copy of input flags.',
                 7, 1.0, 2.3,
                 {'1ST': 0.0, '3RD': 0.0, 'TOT': 0.0, '2ND': 0.0}
                ),
                ('lgtm',
                 1, 1.0, -3.4,
                 {'1ST': 0.0, '3RD': 0.0, 'TOT': 0.0, '2ND': 0.0}
                ),
                ('lgtm',
                 1, 1.0, -3.4,
                 {'1ST': 0.0, '3RD': 0.0, 'TOT': 0.0, '2ND': 0.0}
                ),
                ('policies.',
                 2, 1.0, 8.8,
                 {'1ST': 0.0, '3RD': 0.0, 'TOT': 0.0, '2ND': 0.0}
                ),
                ('policy far from the DevTools creation?',
                 7, 1.0, 5.7,
                 {'1ST': 0.0, '3RD': 0.0, 'TOT': 0.0, '2ND': 0.0}
                ),
                ('to associate the disconnection of the Devtools with the kiosk'
                 ' mode if we set this',
                 15, 0.8666666666666667, 7.6,
                 {'1ST': 0.06666666666666667, '3RD': 0.0,
                  'TOT': 0.06666666666666667, '2ND': 0.0}
                )
            ]
        expected = sorted(expected)

        _ = self.tagger.tag()

        q1 = Q(message__review_id=1259853004)
        q2 = Q(comment__patch__patchset__review_id=1259853004)
        actual = [
                (s.text, s.metrics['length'], s.metrics['type_token_ratio'],
                 s.metrics['flesch_kincaid'], s.metrics['pronoun_density'])
                for s in Sentence.objects.filter(q1 | q2)
            ]
        actual = sorted(actual)
        print(actual)
        for i in range(0, len(expected)):
            self.assertEqual(expected[i], actual[i])
