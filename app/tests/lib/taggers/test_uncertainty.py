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
        expected = [('lgtm', {'words': ['C'], 'sent': 'C'}), ('Looks like you need LGTM from a devtools owner.', {'words': ['C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C'], 'sent': 'C'}), ('lgtm', {'words': ['C'], 'sent': 'C'}), ('The CQ bit was checked by pkasting@chromium.org', {'words': ['C', 'C', 'C', 'C', 'C', 'C', 'C'], 'sent': 'C'}), ('I removed the comment and merged the two conditions.', {'words': ['C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C'], 'sent': 'C'}), ('Done.', {'words': ['C'], 'sent': 'C'}), ('Done.', {'words': ['C'], 'sent': 'C'}), ('policies.', {'words': ['C'], 'sent': 'C'}), ('policy far from the DevTools creation?', {'words': ['C', 'C', 'C', 'C', 'C', 'C'], 'sent': 'C'}), ('LGTM', {'words': ['C'], 'sent': 'C'}), ('Nit: No blank line here', {'words': ['C', 'C', 'C', 'C', 'C'], 'sent': 'C'}), ('pkasting@chromium.org changed reviewers:', {'words': ['C', 'C', 'C'], 'sent': 'C'}), ('+ dgozman@chromium.org, pkasting@google.com', {'words': ['C', 'C', 'C'], 'sent': 'C'}), ("Don't you think that it could make it more difficult", {'words': ['C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C'], 'sent': 'C'}), ('I looked all over the code and I did not saw any place that looked good to set', {'words': ['C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C'], 'sent': 'C'}), ('to associate the disconnection of the Devtools with the kiosk mode if we set this', {'words': ['C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'N', 'C', 'C', 'C'], 'sent': 'N'}), ('Did you have any place in mind where we can set the policy?', {'words': ['C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C'], 'sent': 'C'}), ('+ pkasting@chromium.org', {'words': ['C', 'C'], 'sent': 'C'}), ('frederic.jacob.78@gmail.com changed reviewers:', {'words': ['C', 'C', 'C'], 'sent': 'C'}), ('Nit: Just combine this conditional with the one below.', {'words': ['C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C'], 'sent': 'C'}), ('Code to disconnect the DevTools in kiosk mode.', {'words': ['C', 'C', 'C', 'C', 'C', 'C', 'C', 'C'], 'sent': 'C'}), ("There's no real win from doing so (we save one conditional in one place but have to add code to set the pref elsewhere) and it would make subsequent non-kiosk runs still disable the dev tools unless we added even more code to distinguish why the pref was originally set and then unset it.", {'words': ['C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C'], 'sent': 'C'}), ('The CQ bit was checked by pkasting@chromium.org', {'words': ['C', 'C', 'C', 'C', 'C', 'C', 'C'], 'sent': 'C'}), ('are a copy of input flags.', {'words': ['C', 'C', 'C', 'C', 'C', 'C'], 'sent': 'C'}), ('It work for all OS (Tested it on Win,Osx,Linux) and there are already code to disable the Devtools at this place.', {'words': ['C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C'], 'sent': 'C'}), ('I would not try to set that pref in kiosk mode.', {'words': ['C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C'], 'sent': 'C'}), ('I though that it will fit in chrome/browser/prefs, but all the policies', {'words': ['C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C'], 'sent': 'C'}), ('Is it possible to set the policy |prefs::kDevToolsDisabled| instead in kiosk mode?', {'words': ['C', 'C', 'E', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C'], 'sent': 'E'}), ('I have put it there because it is the central place for the Devtools creation and as such cover all possible case.', {'words': ['C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C'], 'sent': 'C'}), ("You can probably nuke the comment on that since it's just restating the code, rather than trying to expand it.", {'words': ['C', 'C', 'U', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C'], 'sent': 'U'})]
        _ = self.tagger.tag()
        actual = Sentence.objects.filter(review_id=1259853004).values_list('text', 'metrics')
        actual = [(text, metrics['uncertainty']) for text, metrics in actual]
        self.maxDiff = None
        e = sorted(expected)
        a = sorted(actual)
        for i, _ in enumerate(e):
            self.assertEqual(e[i][0], a[i][0])
            self.assertDictEqual(e[i][1], a[i][1])
