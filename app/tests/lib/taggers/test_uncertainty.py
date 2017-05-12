from django import test
from django.conf import settings

from app.lib import loaders, taggers
from app.models import *

from django.core.management import call_command

class UncertaintyTaggerTestCase(test.TransactionTestCase):
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
        self.tagger = taggers.UncertaintyTagger(
                settings, num_processes=2, sentenceObjects=sentObjects
            )

    def test_load(self):
        call_command('sentenceParse')
        expected = [
                (
                    'The CQ bit was checked by pkasting@chromium.org',
                    'X'
                ),
                (
                    'lgtm',
                    'X'
                ),
                (
                    'lgtm',
                    'X'
                ),
                (
                    'Looks like you need LGTM from a devtools owner.',
                    'X'
                ),
                (
                    'The CQ bit was checked by pkasting@chromium.org',
                    'X'
                ),
                (
                    'Done.',
                    'X'
                ),
                (
                    'Done.',
                    'X'
                ),
                (
                    'policies.',
                    'X'
                ),
                (
                    'I would not try to set that pref in kiosk mode.',
                    'X'
                ),
                (
                    'are a copy of input flags.',
                    'X'
                ),
                (
                    'LGTM',
                    'X'
                ),
                (
                    'policy far from the DevTools creation?',
                    'X'
                ),
                (
                    'Nit: No blank line here',
                    'X'
                ),
                (
                    'Nit: Just combine this conditional with the one below.',
                    'X'
                ),
                (
                    'pkasting@chromium.org changed reviewers:',
                    'X'
                ),
                (
                    'frederic.jacob.78@gmail.com changed reviewers:',
                    'X'
                ),
                (
                    '+ dgozman@chromium.org, pkasting@google.com',
                    'X'
                ),
                (
                    'I looked all over the code and I did not saw any place '
                    'that looked good to set',
                    'X'
                ),
                (
                    'to associate the disconnection of the Devtools with the '
                    'kiosk mode if we set this',
                    'X'
                ),
                (
                    "Don't you think that it could make it more difficult",
                    'X'
                ),
                (
                    '+ pkasting@chromium.org',
                    'X'
                ),
                (
                    'Is it possible to set the policy |prefs::kDevToolsDisab'
                    'led| instead in kiosk mode?',
                    'X'
                ),
                (
                    'I removed the comment and merged the two conditions.',
                    'X'
                ),
                (
                    'Did you have any place in mind where we can set the '
                    'policy?',
                    'X'
                ),
                (
                    'Code to disconnect the DevTools in kiosk mode.',
                    'X'
                ),
                (
                    'It work for all OS (Tested it on Win,Osx,Linux) and there'
                    ' are already code to disable the Devtools at this place.',
                    'X'
                ),
                (
                    'I though that it will fit in chrome/browser/prefs, but '
                    'all the policies',
                    'X'
                ),
                (
                    "You can probably nuke the comment on that since it's "
                    "just restating the code, rather than trying to expand it.",
                    'X'
                ),
                (
                    'I have put it there because it is the central place for '
                    'the Devtools creation and as such cover all possible case.',
                    'X'
                ),
                (
                    "There's no real win from doing so (we save one conditional"
                    " in one place but have to add code to set the pref "
                    "elsewhere) and it would make subsequent non-kiosk runs "
                    "still disable the dev tools unless we added even more code"
                    " to distinguish why the pref was originally set and then "
                    "unset it.",
                    'X'
                )
            ]
        _ = self.tagger.tag()
        actual = Sentence.objects.filter(review_id=1259853004).values_list('text', 'metrics')
        actual = [(text, metrics['uncertainty']) for text, metrics in actual]
        print(actual)
        self.maxDiff = None
        e = sorted(expected)
        a = sorted(actual)
        for i, _ in enumerate(e):
            self.assertEqual(e[i][0], a[i][0])
            self.assertDictEqual(e[i][1], a[i][1])
