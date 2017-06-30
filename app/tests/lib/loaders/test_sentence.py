from datetime import datetime

from django import test
from django.conf import settings
from django.db.models import Q

from app.lib import loaders
from app.models import *


class SentenceLoaderTestCase(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        loader = loaders.ReviewLoader(settings, num_processes=2)
        _ = loader.load()
        loader = loaders.MessageLoader(
                settings, num_processes=2, review_ids=[1259853004]
            )
        _ = loader.load()
        loader = loaders.CommentLoader(
                settings, num_processes=2, review_ids=[1259853004]
            )
        _ = loader.load()

    def setUp(self):
        self.loader1 = loaders.SentenceMessageLoader(
                settings, num_processes=2, review_ids=[1259853004]
            )
        self.loader2 = loaders.SentenceCommentLoader(
                settings, num_processes=2, review_ids=[1259853004]
            )

    def test_load(self):
        expected = [
                (1259853004, 'lgtm'),
                (1259853004, 'Looks like you need LGTM from a devtools owner.'),
                (1259853004, 'lgtm'),
                (
                    1259853004,
                    'I removed the comment and merged the two conditions.'
                ),
                (1259853004, 'I would not try to set that pref in kiosk mode.'),
                (
                    1259853004,
                    "There's no real win from doing so (we save one conditional"
                    " in one place but have to add code to set the pref elsewhe"
                    "re) and it would make subsequent non-kiosk runs still disa"
                    "ble the dev tools unless we added even more code to distin"
                    "guish why the pref was originally set and then unset it."
                ),
                (
                    1259853004,
                    'I looked all over the code and I did not saw any place tha'
                    't looked good to set'
                ),
                (1259853004, 'policies.'),
                (
                    1259853004,
                    'I though that it will fit in chrome/browser/prefs, but all'
                    ' the policies'
                ),
                (1259853004, 'are a copy of input flags.'),
                (
                    1259853004,
                    "Don't you think that it could make it more difficult"
                ),
                (
                    1259853004,
                    'to associate the disconnection of the Devtools with the ki'
                    'osk mode if we set this'
                ),
                (1259853004, 'policy far from the DevTools creation?'),
                (
                    1259853004,
                    'Did you have any place in mind where we can set the policy?'
                ),
                (1259853004, 'LGTM'),
                (
                    1259853004,
                    'Is it possible to set the policy |prefs::kDevToolsDisabled'
                    '| instead in kiosk mode?'
                ),
                (1259853004, 'Code to disconnect the DevTools in kiosk mode.'),
                (
                    1259853004,
                    'I have put it there because it is the central place for th'
                    'e Devtools creation and as such cover all possible case.'
                ),
                (
                    1259853004,
                    'It work for all OS (Tested it on Win,Osx,Linux) and there '
                    'are already code to disable the Devtools at this place.'
                )
            ]
        self.assertEqual(len(expected), self.loader1.load())

        actual = Sentence.objects.filter(message__review_id=1259853004) \
                                 .values_list('message__review_id', 'text')
        #print(list(actual))
        self.assertCountEqual(expected, list(actual))
        self.assertListEqual(sorted(expected), sorted(list(actual)))

        # Sub-Test 2
        expected = [
                (1259853004, 'Done.'),
                (1259853004, 'Done.'),
                (
                    1259853004,
                    "You can probably nuke the comment on that since it's just "
                    "restating the code, rather than trying to expand it."
                ),
                (
                    1259853004,
                    'Nit: Just combine this conditional with the one below.'
                ),
                (1259853004, 'Nit: No blank line here')
            ]

        self.assertEqual(len(expected), self.loader2.load())

        actual = Sentence.objects.filter(comment__patch__patchset__review_id=1259853004) \
                                 .values_list('comment__patch__patchset__review_id', 'text')

        self.assertCountEqual(expected, list(actual))
        self.assertListEqual(sorted(expected), sorted(list(actual)))
