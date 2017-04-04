from django import test
from django.conf import settings
from django.db import connection, connections

from app.lib import loaders, taggers
from app.models import *

class SentimentTestCase(test.TransactionTestCase):
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
        self.tagger = taggers.SentimentTagger(
                settings, num_processes=2, sentObjects=sentObjects
            )

    def test_load(self):
        expected = [
                 (
                     'The CQ bit was checked by pkasting@chromium.org',
                     {'neg': 0, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 1}
                 ),
                 (
                     'lgtm',
                     {'neg': 0, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 1}
                 ),
                 (
                     'Looks like you need LGTM from a devtools owner.',
                     {'neg': 0, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 1}
                 ),
                 (
                     'lgtm',
                     {'neg': 0, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 1}
                 ),
                 (
                     'The CQ bit was checked by pkasting@chromium.org',
                     {'neg': 0, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 1}
                 ),
                 (
                     'I removed the comment and merged the two conditions.',
                      {'neg': 1, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 0}
                 ),
                 (
                     'Done.',
                     {'neg': 0, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 1}
                 ),
                 (
                     'Done.',
                     {'neg': 0, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 1}
                 ),
                 (
                     'I would not try to set that pref in kiosk mode.',
                      {'neg': 1, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 0}
                 ),
                 (
                     "There's no real win from doing so (we save one "
                     "conditional in one place but have to add code to set the "
                     "pref elsewhere) and it would make subsequent non-kiosk "
                     "runs still disable the dev tools unless we added even "
                     "more code to distinguish why the pref was originally set "
                     "and then unset it.",
                     {'neg': 0, 'pos': 0, 'vneg': 1, 'vpos': 0, 'neut': 0}
                 ),
                 (
                     'I looked all over the code and I did not saw any place '
                     'that looked good to set',
                     {'neg': 1, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 0}
                 ),
                 (
                     'policies.',
                     {'neg': 0, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 1}
                 ),
                 (
                     'I though that it will fit in chrome/browser/prefs, but '
                     'all the policies',
                     {'neg': 0, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 1}
                 ),
                 (
                     'are a copy of input flags.',
                     {'neg': 1, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 0}
                 ),
                 (
                     "Don't you think that it could make it more difficult",
                     {'neg': 1, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 0}
                 ),
                 (
                     'to associate the disconnection of the Devtools with the '
                     'kiosk mode if we set this',
                     {'neg': 0, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 1}
                 ),
                 (
                     'policy far from the DevTools creation?',
                     {'neg': 0, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 1}
                 ),
                 (
                     'Did you have any place in mind where we can set the '
                     'policy?',
                     {'neg': 1, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 0}
                 ),
                 (
                     'LGTM',
                     {'neg': 0, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 1}
                 ),
                 (
                     'Nit: No blank line here',
                     {'neg': 0, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 1}
                 ),
                 (
                     'Nit: Just combine this conditional with the one below.',
                     {'neg': 1, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 0}
                 ),
                 (
                     "You can probably nuke the comment on that since it's just"
                     " restating the code, rather than trying to expand it.",
                     {'neg': 1, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 0}
                 ),
                 (
                     'pkasting@chromium.org changed reviewers:',
                     {'neg': 0, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 1}
                 ),
                 (
                     'Code to disconnect the DevTools in kiosk mode.',
                     {'neg': 1, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 0}
                 ),
                 (
                     'I have put it there because it is the central place for '
                     'the Devtools creation and as such cover all possible case.',
                     {'neg': 1, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 0}
                 ),
                 (
                     'It work for all OS (Tested it on Win,Osx,Linux) and there '
                     'are already code to disable the Devtools at this place.',
                     {'neg': 1, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 0}
                 ),
                 (
                     '+ dgozman@chromium.org, pkasting@google.com',
                     {'neg': 0, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 1}
                 ),
                 (
                     '+ pkasting@chromium.org',
                     {'neg': 0, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 1}
                 ),
                 (
                     'Is it possible to set the policy |prefs::kDevToolsDisabled'
                     '| instead in kiosk mode?',
                     {'neg': 1, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 0}
                 ),
                 (
                     'frederic.jacob.78@gmail.com changed reviewers:',
                     {'neg': 0, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 1}
                 )
            ]

        _ = self.tagger.tag()
        actual = Sentence.objects.filter(review_id=1259853004).values_list('text', 'metrics')
        actual = [(text, metrics['sentiment']) for text, metrics in actual]
        self.maxDiff = None
        e = sorted(expected)
        a = sorted(actual)
        for i, _ in enumerate(e):
            self.assertEqual(e[i][0], a[i][0])
            self.assertEqual(e[i][1]['neg'], a[i][1]['neg'])
            self.assertEqual(e[i][1]['pos'], a[i][1]['pos'])
            self.assertEqual(e[i][1]['vneg'], a[i][1]['vneg'])
            self.assertEqual(e[i][1]['vpos'], a[i][1]['vpos'])
            self.assertEqual(e[i][1]['neut'], a[i][1]['neut'])

