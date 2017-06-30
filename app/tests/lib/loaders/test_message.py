from datetime import datetime

from django import test
from django.conf import settings

from app.lib import loaders
from app.models import *


def to_datetime(text):
    return datetime.strptime(text, '%Y-%m-%d %H:%M:%S.%f')


class MessageLoaderTestCase(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        loader = loaders.ReviewLoader(settings, num_processes=2)
        _ = loader.load()

    def setUp(self):
        self.loader = loaders.MessageLoader(
                settings, num_processes=2, review_ids=[1259853004]
            )

    def test_load(self):
        expected = [
                (
                    to_datetime('2015-07-31 13:46:30.478330'),
                    'dgozman@chromium.org',
                    'lgtm'
                ),
                (
                    to_datetime('2015-07-31 05:51:11.967330'),
                    'pkasting@chromium.org',
                    'Looks like you need LGTM from a devtools owner.'
                ),
                (
                    to_datetime('2015-07-31 01:42:57.534600'),
                    'pkasting@chromium.org',
                    'lgtm'
                ),
                (
                    to_datetime('2015-07-31 01:06:51.093060'),
                    'frederic.jacob.78@gmail.com',
                    'I removed the comment and merged the two conditions.'
                ),
                (
                    to_datetime('2015-07-30 23:55:34.517080'),
                    'pkasting@chromium.org',
                    "I would not try to set that pref in kiosk mode.  There's n"
                    "o real win from doing so (we save one conditional in one p"
                    "lace but have to add code to set the pref elsewhere) and i"
                    "t would make subsequent non-kiosk runs still disable the d"
                    "ev tools unless we added even more code to distinguish why"
                    " the pref was originally set and then unset it."
                ),
                (
                    to_datetime('2015-07-30 23:51:16.478520'),
                    'frederic.jacob.78@gmail.com',
                    "\n\n\nI looked all over the code and I did not saw any pla"
                    "ce that looked good to set\npolicies. I though that it wil"
                    "l fit in chrome/browser/prefs, but all the policies\nare a"
                    " copy of input flags. Don't you think that it could make i"
                    "t more difficult\nto associate the disconnection of the De"
                    "vtools with the kiosk mode if we set this \npolicy far fro"
                    "m the DevTools creation?\n \nDid you have any place in min"
                    "d where we can set the policy?"
                ),
                (
                    to_datetime('2015-07-30 18:24:22.393890'),
                    'pkasting@chromium.org',
                    'LGTM'
                ),
                (
                    to_datetime('2015-07-30 12:21:22.975630'),
                    'dgozman@chromium.org',
                    'Is it possible to set the policy |prefs::kDevToolsDisabled'
                    '| instead in kiosk mode?'
                ),
                (
                    to_datetime('2015-07-30 10:40:34.029270'),
                    'frederic.jacob.78@gmail.com',
                    'Code to disconnect the DevTools in kiosk mode. I have put '
                    'it there because it is the central place for the Devtools '
                    'creation and as such cover all possible case. It work for '
                    'all OS (Tested it on Win,Osx,Linux) and there are already '
                    'code to disable the Devtools at this place.'
                )
            ]

        actual = self.loader.load()
        self.assertEqual(len(expected), actual, msg='Return')

        actual = list(
                Message.objects.filter(review_id=1259853004)
                .values_list('posted', 'sender', 'text')
            )
        self.assertCountEqual(expected, actual, msg='Data:Message')
