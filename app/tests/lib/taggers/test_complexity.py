from django import test
from django.conf import settings

from app.lib import loaders, taggers
from app.models import *


class ComplexityTaggerTestCase(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        loader = loaders.ReviewLoader(settings, num_processes=2)
        _ = loader.load()
        loader = loaders.MessageLoader(
                settings, num_processes=2, review_ids=[1259853004]
            )
        _ = loader.load()

    def setUp(self):
        self.tagger = taggers.ComplexityTagger(
                settings, num_processes=2, review_ids=[1259853004], zeros=False
            )

    def test_load(self):
        expected = [
                (
                    'frederic.jacob.78@gmail.com changed reviewers:\n+ dgozman'
                    '@chromium.org, pkasting@google.com',
                    {'frazier': 0.8571428571428571,
                     'pdensity': 0.42857142857142855,
                     'yngve': 1.7142857142857142}
                ),
                (
                    'Code to disconnect the DevTools in kiosk mode. I have put'
                    ' it there because it is the central place for the '
                    'Devtools creation and as such cover all possible case. It'
                    ' work for all OS (Tested it on Win,Osx,Linux) and there '
                    'are already code to disable the Devtools at this place.',
                    {'frazier': 0.8333333333333334,
                     'pdensity': 0.32096848401196226,
                     'yngve': 3.15}
                ),
                (
                    'Is it possible to set the policy |prefs::kDevToolsDisable'
                    'd| instead in kiosk mode?',
                    {'frazier': 0.6388888888888888,
                     'pdensity': 0.3333333333333333,
                     'yngve': 3.1666666666666665}
                ),
                (
                    'pkasting@chromium.org changed reviewers:\n+ pkasting@chro'
                    'mium.org',
                    {'frazier': 0.6666666666666666,
                     'pdensity': 0.5,
                     'yngve': 1.8333333333333333}
                ),
                (
                    'LGTM\n\nNit: No blank line here\n\nNit: Just combine this'
                    ' conditional with the one below.  You can probably nuke t'
                    "he comment on that since it's just restating the code, r"
                    'ather than trying to expand it.',
                    {'frazier': 1.0,
                     'pdensity': 0.427536231884058,
                     'yngve': 2.5609756097560976}
                ),
                (
                    '\nI looked all over the code and I did not saw any place '
                    'that looked good to set\npolicies. I though that it will '
                    'fit in chrome/browser/prefs, but all the policies\nare a '
                    "copy of input flags. Don't you think that it could make "
                    'it more difficult\nto associate the disconnection of the '
                    'Devtools with the kiosk mode if we set this \npolicy far '
                    'from the DevTools creation?\n \nDid you have any place in'
                    ' mind where we can set the policy?',
                    {'frazier': 0.8505747126436781,
                     'pdensity': 0.41320346320346324,
                     'yngve': 2.632183908045977}
                ),
                (
                    "I would not try to set that pref in kiosk mode.  There's "
                    'no real win from doing so (we save one conditional in one '
                    'place but have to add code to set the pref elsewhere) and '
                    'it would make subsequent non-kiosk runs still disable the '
                    'dev tools unless we added even more code to distinguish '
                    'why the pref was originally set and then unset it.',
                    {'frazier': 1.0071428571428571,
                     'pdensity': 0.4410919540229885,
                     'yngve': 3.857142857142857}
                ),
                (
                    'I removed the comment and merged the two conditions.\n\nD'
                    'one.\n\nDone.',
                    {'frazier': 0.6785714285714286,
                     'pdensity': 0.4666666666666666,
                     'yngve': 1.7857142857142858}
                ),
                (
                    'The CQ bit was checked by pkasting@chromium.org',
                    {'frazier': 0.9285714285714286,
                     'pdensity': 0.42857142857142855,
                     'yngve': 1.2857142857142858}
                ),
                (
                    'lgtm',
                    {'frazier': 1.0, 'pdensity': 0.0, 'yngve': 0.0}
                ),
                (
                    'Looks like you need LGTM from a devtools owner.',
                    {'frazier': 0.85,
                     'pdensity': 0.4,
                     'yngve': 2.0}
                ),
                (
                    'lgtm',
                    {'frazier': 1.0, 'pdensity': 0.0, 'yngve': 0.0}
                ),
                (
                    'The CQ bit was checked by pkasting@chromium.org',
                    {'frazier': 0.9285714285714286,
                     'pdensity': 0.42857142857142855,
                     'yngve': 1.2857142857142858}
                ),
            ]

        _ = self.tagger.tag()
        actual = list(
                Message.objects.filter(review__id=1259853004)
                .values_list('text', 'complexity')
            )
        self.maxDiff = None
        e = sorted(expected)
        a = sorted(actual)
        for i, _ in enumerate(e):
            self.assertEqual(e[i][0], a[i][0])
            self.assertEqual(e[i][1]['yngve'], a[i][1]['yngve'])
            self.assertEqual(e[i][1]['frazier'], a[i][1]['frazier'])
            self.assertEqual(e[i][1]['pdensity'], a[i][1]['pdensity'])
