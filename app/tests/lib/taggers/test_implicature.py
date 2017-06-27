from django import test
from django.conf import settings
from django.db import connections

from app.lib import loaders, taggers
from app.models import *

from django.core.management import call_command


class ImplicatureTaggerTestCase(test.TransactionTestCase):
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

        connections.close_all()  # Hack

        sentObjects = Sentence.objects.filter(message__review_id=1259853004)
        self.tagger = taggers.ImplicatureTagger(
                settings, num_processes=2, sentenceObjects=sentObjects
            )

    def test_load(self):
        expected = [
                (
                    'The CQ bit was checked by pkasting@chromium.org',
                    {
                        'implicative': 0.921974070462844,
                        'unimplicative': 0.07802592953715604
                    }
                ),
                (
                    'lgtm',
                    {
                        'implicative': 0.7201292384779764,
                        'unimplicative': 0.2798707615220236
                    }
                ),
                (
                    'Looks like you need LGTM from a devtools owner.',
                    {
                        'implicative': 0.4726080230704487,
                        'unimplicative': 0.5273919769295513
                    }
                ),
                (
                    'lgtm',
                    {
                        'implicative': 0.7201292384779764,
                        'unimplicative': 0.2798707615220236
                    }
                ),
                (
                    'The CQ bit was checked by pkasting@chromium.org',
                    {
                        'implicative': 0.921974070462844,
                        'unimplicative': 0.07802592953715604
                    }
                ),
                (
                    'Done.',
                    {
                        'implicative': 0.8318886704807316,
                        'unimplicative': 0.16811132951926844
                    }
                ),
                (
                    'Done.',
                    {
                        'implicative': 0.8318886704807316,
                        'unimplicative': 0.16811132951926844
                    }
                ),
                (
                    'policies.',
                    {
                        'implicative': 0.7772156694129054,
                        'unimplicative': 0.22278433058709457
                    }
                ),
                (
                    'are a copy of input flags.',
                    {
                        'implicative': 0.40550244046287315,
                        'unimplicative': 0.5944975595371269
                    }
                ),
                (
                    "Don't you think that it could make it more difficult",
                    {
                        'implicative': 0.04658133951362846,
                        'unimplicative': 0.9534186604863716
                    }
                ),
                (
                    'policy far from the DevTools creation?',
                    {
                        'implicative': 0.30825806905293995,
                        'unimplicative': 0.69174193094706
                    }
                ),
                (
                    'LGTM',
                    {
                        'implicative': 0.7156971686486916,
                        'unimplicative': 0.2843028313513084
                    }
                ),
                (
                    '+ pkasting@chromium.org',
                    {
                        'implicative': 0.8803745818748707,
                        'unimplicative': 0.11962541812512928
                    }
                ),
                (
                    'Code to disconnect the DevTools in kiosk mode.',
                    {
                        'implicative': 0.8150053394290124,
                        'unimplicative': 0.18499466057098757
                    }
                ),
                (
                    'frederic.jacob.78@gmail.com changed reviewers:',
                    {
                        'implicative': 0.9931265821378343,
                        'unimplicative': 0.006873417862165665
                    }
                ),
                (
                    'I removed the comment and merged the two conditions.',
                    {
                        'implicative': 0.5913358898182716,
                        'unimplicative': 0.40866411018172843
                    }
                ),
                (
                    'I though that it will fit in chrome/browser/prefs, but '
                    'all the policies',
                    {
                        'implicative': 0.8951565484583148,
                        'unimplicative': 0.10484345154168517
                    }
                ),
                (
                    'Did you have any place in mind where we can set the '
                    'policy?',
                    {
                        'implicative': 0.05652111937110279,
                        'unimplicative': 0.9434788806288972
                    }
                ),
                (
                    'pkasting@chromium.org changed reviewers:',
                    {
                        'implicative': 0.9525396766998352,
                        'unimplicative': 0.04746032330016481
                    }
                ),
                (
                    'Nit: No blank line here',
                    {
                        'implicative': 0.21041377243940823,
                        'unimplicative': 0.7895862275605918
                    }
                ),
                (
                    'to associate the disconnection of the Devtools with the '
                    'kiosk mode if we set this',
                    {
                        'implicative': 0.594860852716583,
                        'unimplicative': 0.40513914728341704
                    }
                ),
                (
                    'Nit: Just combine this conditional with the one below.',
                    {
                        'implicative': 0.5184391184392932,
                        'unimplicative': 0.48156088156070675
                    }
                ),
                (
                    'I have put it there because it is the central place for '
                    'the Devtools creation and as such cover all possible '
                    'case.',
                    {
                        'implicative': 0.8205685717773425,
                        'unimplicative': 0.17943142822265745
                    }
                ),
                (
                    'It work for all OS (Tested it on Win,Osx,Linux) and '
                    'there are already code to disable the Devtools at this '
                    'place.',
                    {
                        'implicative': 0.3509005554903233,
                        'unimplicative': 0.6490994445096767
                    }
                ),
                (
                    'I would not try to set that pref in kiosk mode.',
                    {
                        'implicative': 0.1006925390686917,
                        'unimplicative': 0.8993074609313083
                    }
                ),
                (
                    'I looked all over the code and I did not saw any place '
                    'that looked good to set',
                    {
                        'implicative': 0.0165104766351752,
                        'unimplicative': 0.9834895233648248
                    }
                ),
                (
                    '+ dgozman@chromium.org, pkasting@google.com',
                    {
                        'implicative': 0.957989012582676,
                        'unimplicative': 0.04201098741732401
                    }
                ),
                (
                    "You can probably nuke the comment on that since it's "
                    "just restating the code, rather than trying to expand "
                    "it.",
                    {
                        'implicative': 0.07351337522645907,
                        'unimplicative': 0.9264866247735409
                    }
                ),
                (
                    'Is it possible to set the policy '
                    '|prefs::kDevToolsDisabled| instead in kiosk mode?',
                    {
                        'implicative': 0.3321551800433818,
                        'unimplicative': 0.6678448199566183
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
                        'implicative': 0.8334144220444127,
                        'unimplicative': 0.16658557795558726
                    }
                )
            ]
        expected = {text: metrics for (text, metrics) in expected}

        _ = self.tagger.tag()

        actual = {
                sentence.text: sentence.metrics['implicature']
                for sentence in Sentence.objects
                                        .filter(message__review_id=1259853004)
            }
        for text in expected:
            self.assertTrue(text in actual)
            for metric in ['implicative', 'unimplicative']:
                self.assertAlmostEqual(
                        expected[text][metric], actual[text][metric],
                        msg='{}:{}'.format(metric, text)
                    )
