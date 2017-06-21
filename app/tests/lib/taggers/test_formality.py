
from django import test
from django.conf import settings

from app.lib import loaders, taggers
from app.models import *

from django.core.management import call_command

class FormalityTaggerTestCase(test.TransactionTestCase):
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

        sentObjects = Sentence.objects.filter(review_id=1259853004).iterator()
        self.tagger = taggers.FormalityTagger(
                settings, num_processes=2, sentenceObjects=sentObjects
            )

    def test_load(self):
        call_command('sentenceParse')
        expected = [
                (
                    'The CQ bit was checked by pkasting@chromium.org',
                    {
                        'formal': 0.6007579530375531,
                        'informal': 0.3992420469624469
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
                    'Looks like you need LGTM from a devtools owner.',
                    {
                        'formal': 0.7322925478557456,
                        'informal': 0.2677074521442544
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
                    'The CQ bit was checked by pkasting@chromium.org',
                    {
                        'formal': 0.6007579530375531,
                        'informal': 0.3992420469624469
                    }
                ),
                (
                    'Done.',
                    {
                        'formal': 0.9580664517766108,
                        'informal': 0.04193354822338924
                    }
                ),
                (
                    'Done.',
                    {
                        'formal': 0.9580664517766108,
                        'informal': 0.04193354822338924
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
                    '+ pkasting@chromium.org',
                    {
                        'formal': 0.9940912060619657,
                        'informal': 0.00590879393803434
                    }
                ),
                (
                    'Code to disconnect the DevTools in kiosk mode.',
                    {
                        'formal': 0.8160727934429036,
                        'informal': 0.18392720655709638
                    }
                ),
                (
                    'frederic.jacob.78@gmail.com changed reviewers:',
                    {
                        'formal': 0.9796474653272814,
                        'informal': 0.02035253467271858
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
                        'formal': 0.9590009884696147,
                        'informal': 0.04099901153038532
                    }
                ),
                (
                    'pkasting@chromium.org changed reviewers:',
                    {
                        'formal': 0.9675266586732113,
                        'informal': 0.032473341326788696
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
                        'formal': 0.8180145393810242,
                        'informal': 0.1819854606189758
                    }
                ),
                (
                    'I have put it there because it is the central place for '
                    'the Devtools creation and as such cover all possible case.',
                    {
                        'formal': 0.010657033433948061,
                        'informal': 0.9893429665660519
                    }
                ),
                (
                    'It work for all OS (Tested it on Win,Osx,Linux) and there '
                    'are already code to disable the Devtools at this place.',
                    {
                        'formal': 0.9470493238203167,
                        'informal': 0.0529506761796833
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
                    '+ dgozman@chromium.org, pkasting@google.com',
                    {
                        'formal': 0.9283786045529506,
                        'informal': 0.07162139544704937
                    }
                ),
                (
                    "You can probably nuke the comment on that since it's "
                    "just restating the code, rather than trying to expand it.",
                    {
                        'formal': 0.9352595261512059,
                        'informal': 0.06474047384879411
                    }
                ),
                (
                    'Is it possible to set the policy |prefs::kDevToolsDisabled'
                    '| instead in kiosk mode?',
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
                        'formal': 0.07884819999728891,
                        'informal': 0.9211518000027111
                    }
                )
            ]

        _ = self.tagger.tag()
        actual = Sentence.objects.filter(review_id=1259853004).values_list('text', 'metrics')
        actual = [(text, metrics['formality']) for text, metrics in actual]
        self.maxDiff = None
        e = sorted(expected)
        a = sorted(actual)
        for i, _ in enumerate(e):
            self.assertEqual(e[i][0], a[i][0])
            self.assertDictEqual(e[i][1], a[i][1])
