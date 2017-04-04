from django import test
from django.conf import settings

from app.lib import loaders, taggers
from app.models import *

from django.core.management import call_command

class ComplexityTaggerTestCase(test.TransactionTestCase):
    def setUp(self):
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

        sentObjects = Sentence.objects.filter(review_id=1259853004).iterator()
        self.tagger = taggers.ComplexityTagger(
                settings, num_processes=2, sentObjects=sentObjects
            )

    def test_load(self):
        call_command('sentenceParse')
        expected = [
                (
                    'The CQ bit was checked by pkasting@chromium.org',
                    {
                        'frazier': 0.9285714285714286,
                        'pdensity': 0.42857142857142855,
                        'yngve': 1.2857142857142858,
                        'cdensity': 2.5
                    }
                ),
                (
                    'lgtm',
                    {
                        'frazier': 1.0, 'pdensity': 0.0,
                        'yngve': 0.0, 'cdensity': 0.0
                    }
                ),
                (
                    'lgtm',
                    {
                        'frazier': 1.0, 'pdensity': 0.0,
                        'yngve': 0.0, 'cdensity': 0.0
                    }
                ),
                (
                    'Looks like you need LGTM from a devtools owner.',
                    {
                        'frazier': 0.85, 'pdensity': 0.4,
                        'yngve': 2.0, 'cdensity': 1.25
                    }
                ),
                (
                    'The CQ bit was checked by pkasting@chromium.org',
                    {
                        'frazier': 0.9285714285714286,
                        'pdensity': 0.42857142857142855,
                        'yngve': 1.2857142857142858,
                        'cdensity': 2.5
                    }
                ),
                (
                    'Done.',
                    {
                        'frazier': 0.5, 'pdensity': 0.5,
                        'yngve': 0.5, 'cdensity': 0.0
                    }
                ),
                (
                    'Done.',
                    {
                        'frazier': 0.5, 'pdensity': 0.5,
                        'yngve': 0.5, 'cdensity': 0.0
                    }
                ),
                (
                    'policies.',
                    {
                        'frazier': 0.5, 'pdensity': 0.0,
                        'yngve': 0.5, 'cdensity': 0.0
                    }
                ),
                (
                    'policy far from the DevTools creation?',
                    {
                        'frazier': 0.8571428571428571,
                        'pdensity': 0.2857142857142857,
                        'yngve': 1.7142857142857142,
                        'cdensity': 2.0
                    }
                ),
                (
                    'Did you have any place in mind where we can set the policy?',
                    {
                        'frazier': 0.9285714285714286,
                        'pdensity': 0.42857142857142855,
                        'yngve': 2.2857142857142856,
                        'cdensity': 0.8571428571428571
                    }
                ),
                (
                    'LGTM',
                    {
                        'frazier': 1.0, 'pdensity': 0.0,
                        'yngve': 0.0, 'cdensity': 0.0
                    }
                ),
                (
                    'Nit: No blank line here',
                    {
                        'frazier': 0.8333333333333334,
                        'pdensity': 0.3333333333333333,
                        'yngve': 1.5, 'cdensity': 4.0
                    }
                ),
                (
                    'pkasting@chromium.org changed reviewers:',
                    {
                        'frazier': 0.75, 'pdensity': 0.5,
                        'yngve': 1.5, 'cdensity': 0.0
                    }
                ),
                (
                    '+ pkasting@chromium.org',
                    {
                        'frazier': 1.0, 'pdensity': 0.5,
                        'yngve': 0.5, 'cdensity': 1.0
                    }
                ),
                (
                    '+ dgozman@chromium.org, pkasting@google.com',
                    {
                        'frazier': 0.6666666666666666,
                        'pdensity': 0.3333333333333333,
                        'yngve': 0.6666666666666666,
                        'cdensity': 2.0
                    }
                ),
                (
                    'are a copy of input flags.',
                    {
                        'frazier': 0.9285714285714286,
                        'pdensity': 0.2857142857142857,
                        'yngve': 1.7142857142857142,
                        'cdensity': 2.0
                    }
                ),
                (
                    "Don't you think that it could make it more difficult",
                    {
                        'frazier': 1.0454545454545454,
                        'pdensity': 0.5454545454545454,
                        'yngve': 1.1818181818181819,
                        'cdensity': 1.2
                    }
                ),
                (
                    'I though that it will fit in chrome/browser/prefs, but all'
                    ' the policies',
                    {
                        'frazier': 0.7307692307692307,
                        'pdensity': 0.46153846153846156,
                        'yngve': 2.6153846153846154,
                        'cdensity': 0.3333333333333333
                    }
                ),
                (
                    'Nit: Just combine this conditional with the one below.',
                    {
                        'frazier': 0.9545454545454546,
                        'pdensity': 0.45454545454545453,
                        'yngve': 2.272727272727273,
                        'cdensity': 0.8
                    }
                ),
                (
                    'to associate the disconnection of the Devtools with the '
                    'kiosk mode if we set this',
                    {
                        'frazier': 0.9333333333333333,
                        'pdensity': 0.4, 'yngve': 2.0,
                        'cdensity': 0.6666666666666666
                    }
                ),
                (
                    'frederic.jacob.78@gmail.com changed reviewers:',
                    {
                        'frazier': 0.75, 'pdensity': 0.5,
                        'yngve': 1.5, 'cdensity': 0.0
                    }
                ),
                (
                    'Code to disconnect the DevTools in kiosk mode.',
                    {
                        'frazier': 0.8333333333333334,
                        'pdensity': 0.2222222222222222,
                        'yngve': 1.8888888888888888,
                        'cdensity': 1.6666666666666667
                    }
                ),
                (
                    'I have put it there because it is the central place for '
                    'the Devtools creation and as such cover all possible case.',
                    {
                        'frazier': 0.717391304347826,
                        'pdensity': 0.34782608695652173,
                        'yngve': 3.0869565217391304,
                        'cdensity': 1.2
                    }
                ),
                (
                    'I would not try to set that pref in kiosk mode.',
                    {
                        'frazier': 1.125, 'pdensity': 0.4166666666666667,
                        'yngve': 1.8333333333333333, 'cdensity': 1.2
                    }
                ),
                (
                    'I removed the comment and merged the two conditions.',
                    {
                        'frazier': 0.75, 'pdensity': 0.4,
                        'yngve': 2.3, 'cdensity': 0.8
                    }
                ),
                (
                    'I looked all over the code and I did not saw any place '
                    'that looked good to set',
                    {
                        'frazier': 1.0833333333333333,
                        'pdensity': 0.4444444444444444,
                        'yngve': 1.6666666666666667,
                        'cdensity': 1.0
                    }
                ),
                (
                    "There's no real win from doing so (we save one conditional"
                    " in one place but have to add code to set the pref "
                    "elsewhere) and it would make subsequent non-kiosk runs "
                    "still disable the dev tools unless we added even more code"
                    " to distinguish why the pref was originally set and then "
                    "unset it.",
                    {
                        'frazier': 0.9827586206896551,
                        'pdensity': 0.46551724137931033,
                        'yngve': 4.275862068965517,
                        'cdensity': 1.5
                    }
                ),
                (
                    'Is it possible to set the policy |prefs::kDevToolsDisabled'
                    '| instead in kiosk mode?',
                    {
                        'frazier': 0.6388888888888888,
                        'pdensity': 0.3333333333333333,
                        'yngve': 3.1666666666666665,
                        'cdensity': 1.5
                    }
                ),
                (
                    "You can probably nuke the comment on that since it's just"
                    " restating the code, rather than trying to expand it.",
                    {
                        'frazier': 1.0217391304347827,
                        'pdensity': 0.5217391304347826,
                        'yngve': 2.4782608695652173,
                        'cdensity': 0.9090909090909091
                    }
                ),
                (
                    'It work for all OS (Tested it on Win,Osx,Linux) and there'
                    ' are already code to disable the Devtools at this place.',
                    {
                        'frazier': 0.9285714285714286,
                        'pdensity': 0.39285714285714285,
                        'yngve': 3.607142857142857,
                        'cdensity': 1.0909090909090908
                    }
                )
            ]

        _ = self.tagger.tag()
        actual = Sentence.objects.filter(review_id=1259853004).values_list('text', 'metrics')
        actual = [(text, metrics['complexity']) for text, metrics in actual]
        self.maxDiff = None
        e = sorted(expected)
        a = sorted(actual)
        for i, _ in enumerate(e):
            self.assertEqual(e[i][0], a[i][0])
            self.assertEqual(e[i][1]['yngve'], a[i][1]['yngve'])
            self.assertEqual(e[i][1]['frazier'], a[i][1]['frazier'])
            self.assertEqual(e[i][1]['pdensity'], a[i][1]['pdensity'])
            self.assertEqual(e[i][1]['cdensity'], a[i][1]['cdensity'])
