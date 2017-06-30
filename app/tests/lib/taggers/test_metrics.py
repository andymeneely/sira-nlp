from django import test
from django.conf import settings
from django.db import connections
from django.db.models import Q

from app.lib import loaders, taggers
from app.models import *

from django.core.management import call_command


class MetricsTaggerTestCase(test.TransactionTestCase):
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
        self.tagger = taggers.MetricsTagger(
                settings, num_processes=2, sentenceObjects=sentObjects,
                metrics=['formality', 'informativeness', 'implicature']
            )

    def test_load(self):
        expected = [
                (
                    'lgtm',
                    {
                        'formal': 0.9554786484216474,
                        'informal': 0.044521351578352575
                    }
                ),
                (
                    'Looks like you need LGTM from a devtools owner.',
                    {
                        'formal': 0.7236392495196992,
                        'informal': 0.2763607504803
                    }
                ),
                (
                    'lgtm',
                    {
                        'formal': 0.9554786484216474,
                        'informal': 0.044521351578352575
                    }
                ),
                (
                    'Done.',
                    {
                        'formal': 0.9560280075705169,
                        'informal': 0.04397199242948313
                    }
                ),
                (
                    'Done.',
                    {
                        'formal': 0.9560280075705169,
                        'informal': 0.04397199242948313
                    }
                ),
                (
                    'policies.',
                    {
                        'formal': 0.8759002711822014,
                        'informal': 0.12409972881779863
                    }
                ),
                (
                    'are a copy of input flags.',
                    {
                        'formal': 0.7587524581525787,
                        'informal': 0.24124754184742125
                    }
                ),
                (
                    "Don't you think that it could make it more difficult",
                    {
                        'formal': 0.9144682647190996,
                        'informal': 0.08553173528090041
                    }
                ),
                (
                    'policy far from the DevTools creation?',
                    {
                        'formal': 0.8047949436225111,
                        'informal': 0.19520505637748886
                    }
                ),
                (
                    'LGTM',
                    {
                        'formal': 0.9285427839666966,
                        'informal': 0.07145721603330335
                    }
                ),
                (
                    'Code to disconnect the DevTools in kiosk mode.',
                    {
                        'formal': 0.8133996729254985,
                        'informal': 0.18660032707450147
                    }
                ),
                (
                    'I removed the comment and merged the two conditions.',
                    {
                        'formal': 0.4907094516421489,
                        'informal': 0.5092905483578511
                    }
                ),
                (
                    'I though that it will fit in chrome/browser/prefs, but '
                    'all the policies',
                    {
                        'formal': 0.9639167742574419,
                        'informal': 0.03608322574255807
                    }
                ),
                (
                    'Did you have any place in mind where we can set the '
                    'policy?',
                    {
                        'formal': 0.9578748126664057,
                        'informal': 0.04212518733359427
                    }
                ),
                (
                    'Nit: No blank line here',
                    {
                        'formal': 0.9747818625399854,
                        'informal': 0.025218137460014556
                    }
                ),
                (
                    'to associate the disconnection of the Devtools with the '
                    'kiosk mode if we set this',
                    {
                        'formal': 0.9486603128100037,
                        'informal': 0.051339687189996264
                    }
                ),
                (
                    'Nit: Just combine this conditional with the one below.',
                    {
                        'formal': 0.8324767352560595,
                        'informal': 0.16752326474394053
                    }
                ),
                (
                    'I have put it there because it is the central place for '
                    'the Devtools creation and as such cover all possible '
                    'case.',
                    {
                        'formal': 0.010657033433948061,
                        'informal': 0.9893429665660519
                    }
                ),
                (
                    'It work for all OS (Tested it on Win,Osx,Linux) and '
                    'there are already code to disable the Devtools at this '
                    'place.',
                    {
                        'formal': 0.9514776006037199,
                        'informal': 0.04852239939628
                    }
                ),
                (
                    'I would not try to set that pref in kiosk mode.',
                    {
                        'formal': 0.9866015552582938,
                        'informal': 0.01339844474170615
                    }
                ),
                (
                    'I looked all over the code and I did not saw any place '
                    'that looked good to set',
                    {
                        'formal': 0.9465330119933556,
                        'informal': 0.0534669880066444
                    }
                ),
                (
                    "You can probably nuke the comment on that since it's "
                    "just restating the code, rather than trying to expand "
                    "it.",
                    {
                        'formal': 0.9282941109660318,
                        'informal': 0.07170588903396824
                    }
                ),
                (
                    'Is it possible to set the policy '
                    '|prefs::kDevToolsDisabled| instead in kiosk mode?',
                    {
                        'formal': 0.9070844366402679,
                        'informal': 0.09291556335973206
                    }
                ),
                (
                    "There's no real win from doing so (we save one "
                    "conditional in one place but have to add code to set the "
                    "pref elsewhere) and it would make subsequent non-kiosk "
                    "runs still disable the dev tools unless we added even "
                    "more code to distinguish why the pref was originally set "
                    "and then unset it.",
                    {
                        'formal': 0.077391311892486,
                        'informal': 0.922608688107514
                    }
                )
            ]
        expected = sorted(expected)

        _ = self.tagger.tag()

        q1 = Q(message__review_id=1259853004)
        q2 = Q(comment__patch__patchset__review_id=1259853004)
        actual = [
                (sentence.text, sentence.metrics['formality'])
                for sentence in Sentence.objects.filter(q1 | q2)
            ]
        actual = sorted(actual)
        for index in range(0, len(expected)):
            etext, emetrics = expected[index]
            atext, ametrics = actual[index]
            self.assertEqual(etext, atext)
            for metric in ['formal', 'informal']:
                self.assertAlmostEqual(
                        emetrics[metric], ametrics[metric],
                        msg='{}:{}'.format(metric, etext),
                        places=7
                    )
