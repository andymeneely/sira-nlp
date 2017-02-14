from django import test
from django.conf import settings

from app.lib import loaders, taggers
from app.models import *


class BugLoaderTestCase(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        loader = loaders.ReviewLoader(settings, num_processes=2)
        _ = loader.load()
        loader = loaders.MessageLoader(
                settings, num_processes=2, review_ids=[1259853004]
            )
        _ = loader.load()

    def setUp(self):
        self.tagger = taggers.SentimentTagger(
                settings, num_processes=2, review_ids=[1259853004]
            )

    def test_load(self):
        expected = [
                (
                    'frederic.jacob.78@gmail.com changed reviewers:\n+ dgozman'
                    '@chromium.org, pkasting@google.com',
                    {'vneg': 0, 'neg': 1, 'neut': 0, 'pos': 0, 'vpos': 0}
                ),
                (
                    'Code to disconnect the DevTools in kiosk mode. I have put'
                    ' it there because it is the central place for the Devtool'
                    's creation and as such cover all possible case. It work f'
                    'or all OS (Tested it on Win,Osx,Linux) and there are alre'
                    'ady code to disable the Devtools at this place.',
                    {'vneg': 0, 'neg': 3, 'neut': 0, 'pos': 0, 'vpos': 0}
                ),
                (
                    'Is it possible to set the policy |prefs::kDevToolsDisable'
                    'd| instead in kiosk mode?',
                    {'vneg': 0, 'neg': 1, 'neut': 0, 'pos': 0, 'vpos': 0}
                ),
                (
                    'pkasting@chromium.org changed reviewers:\n+ pkasting@chro'
                    'mium.org',
                    {'vneg': 0, 'neg': 0, 'neut': 1, 'pos': 0, 'vpos': 0}
                ),
                (
                    'LGTM\n\nNit: No blank line here\n\nNit: Just combine this'
                    ' conditional with the one below.  You can probably nuke t'
                    'he comment on that since it\'s just restating the code, r'
                    'ather than trying to expand it.',
                    {'vneg': 0, 'neg': 2, 'neut': 0, 'pos': 0, 'vpos': 0}
                ),
                (
                    '\nI looked all over the code and I did not saw any place '
                    'that looked good to set\npolicies. I though that it will '
                    'fit in chrome/browser/prefs, but all the policies\nare a '
                    'copy of input flags. Don\'t you think that it could make '
                    'it more difficult\nto associate the disconnection of the '
                    'Devtools with the kiosk mode if we set this \npolicy far '
                    'from the DevTools creation?\n \nDid you have any place in'
                    ' mind where we can set the policy?',
                    {'vneg': 0, 'neg': 4, 'neut': 0, 'pos': 0, 'vpos': 0}
                ),
                (
                    'I would not try to set that pref in kiosk mode.  There\'s'
                    ' no real win from doing so (we save one conditional in on'
                    'e place but have to add code to set the pref elsewhere) a'
                    'nd it would make subsequent non-kiosk runs still disable '
                    'the dev tools unless we added even more code to distingui'
                    'sh why the pref was originally set and then unset it.',
                    {'vneg': 1, 'neg': 1, 'neut': 0, 'pos': 0, 'vpos': 0}
                ),
                (
                    'I removed the comment and merged the two conditions.\n\nD'
                    'one.\n\nDone.',
                    {'vneg': 0, 'neg': 1, 'neut': 2, 'pos': 0, 'vpos': 0}
                ),
                (
                    'The CQ bit was checked by pkasting@chromium.org',
                    {'vneg': 0, 'neg': 0, 'neut': 1, 'pos': 0, 'vpos': 0}
                ),
                (
                    'lgtm',
                    {'vneg': 0, 'neg': 0, 'neut': 1, 'pos': 0, 'vpos': 0}
                ),
                (
                    'Looks like you need LGTM from a devtools owner.',
                    {'vneg': 0, 'neg': 0, 'neut': 1, 'pos': 0, 'vpos': 0}
                ),
                (
                    'lgtm',
                    {'vneg': 0, 'neg': 0, 'neut': 1, 'pos': 0, 'vpos': 0}
                ),
                (
                    'The CQ bit was checked by pkasting@chromium.org',
                    {'vneg': 0, 'neg': 0, 'neut': 1, 'pos': 0, 'vpos': 0}
                )
            ]

        _ = self.tagger.tag()
        actual = list(
                Message.objects.filter(review__id=1259853004)
                .values_list('text', 'sentiment')
            )
        self.maxDiff = None
        self.assertCountEqual(expected, actual)
