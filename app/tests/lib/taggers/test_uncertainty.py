from django import test
from django.conf import settings
from django.db import connections

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
        loader = loaders.TokenLoader(
                settings, num_processes=2, review_ids=[1259853004]
            )
        _ = loader.load()

        connections.close_all()  # Hack

        sentObjects = Sentence.objects.filter(message__review_id=1259853004)
        self.tagger = taggers.UncertaintyTagger(
                settings, num_processes=2, sentenceObjects=sentObjects,
                root_type='stem'
            )

    def test_load(self):
        expected = [
                ('The CQ bit was checked by pkasting@chromium.org', False),
                ('lgtm', False),
                ('lgtm', False),
                ('Looks like you need LGTM from a devtools owner.', False),
                ('The CQ bit was checked by pkasting@chromium.org', False),
                ('Done.', False),
                ('Done.', False),
                ('policies.', False),
                (
                    'I would not try to set that pref in kiosk mode.',
                    True  # Uncertain: "would"
                ),
                ('are a copy of input flags.', False),
                ('LGTM', False),
                ('policy far from the DevTools creation?', False),
                ('Nit: No blank line here', False),
                (
                    'Nit: Just combine this conditional with the one below.',
                    False
                ),
                ('pkasting@chromium.org changed reviewers:', False),
                ('frederic.jacob.78@gmail.com changed reviewers:', False),
                ('+ dgozman@chromium.org, pkasting@google.com', False),
                (
                    'I looked all over the code and I did not saw any place '
                    'that looked good to set',
                    False
                ),
                (
                    'to associate the disconnection of the Devtools with the '
                    'kiosk mode if we set this',
                    True  # Uncertain: "if"
                ),
                (
                    "Don't you think that it could make it more difficult",
                    True  # Uncertain: "think"
                ),
                ('+ pkasting@chromium.org', False),
                (
                    'Is it possible to set the policy |prefs::kDevToolsDisab'
                    'led| instead in kiosk mode?',
                    False
                ),
                (
                    'I removed the comment and merged the two conditions.',
                    False
                ),
                (
                    'Did you have any place in mind where we can set the '
                    'policy?',
                    False
                ),
                ('Code to disconnect the DevTools in kiosk mode.', False),
                (
                    'It work for all OS (Tested it on Win,Osx,Linux) and there'
                    ' are already code to disable the Devtools at this place.',
                    False
                ),
                (
                    'I though that it will fit in chrome/browser/prefs, but '
                    'all the policies',
                    False
                ),
                (
                    "You can probably nuke the comment on that since it's just"
                    " restating the code, rather than trying to expand it.",
                    True  # Uncertain: "probably"
                ),
                (
                    'I have put it there because it is the central place for '
                    'the Devtools creation and as such cover all possible '
                    'case.',
                    False
                ),
                (
                    "There's no real win from doing so (we save one "
                    "conditional in one place but have to add code to set the "
                    "pref elsewhere) and it would make subsequent non-kiosk "
                    "runs still disable the dev tools unless we added even "
                    "more code to distinguish why the pref was originally set "
                    "and then unset it.",
                    False
                ),
            ]
        _ = self.tagger.tag()
        actual = [
                (sentence.text, sentence.metrics['uncertain'])
                for sentence in Sentence.objects
                                        .filter(message__review_id=1259853004)
            ]
        self.assertCountEqual(expected, actual)
