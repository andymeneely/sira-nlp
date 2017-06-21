
from django import test
from django.conf import settings

from app.lib import loaders, taggers
from app.models import *

from django.core.management import call_command

class InformativenessTaggerTestCase(test.TransactionTestCase):
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
        self.tagger = taggers.InformativenessTagger(
                settings, num_processes=2, sentenceObjects=sentObjects
            )

    def test_load(self):
        call_command('sentenceParse')
        expected = [
                (
                    'The CQ bit was checked by pkasting@chromium.org',
                    {
                        'informative': 0.013371042999968188,
                        'uninformative': 0.9866289570000318
                    }
                ),
                (
                    'lgtm',
                    {
                        'informative': 0.9044983523150818,
                        'uninformative': 0.0955016476849182
                    }
                ),
                (
                    'Looks like you need LGTM from a devtools owner.',
                    {
                        'informative': 0.07781988649812836,
                        'uninformative': 0.9221801135018717
                    }
                ),
                (
                    'lgtm',
                    {
                        'informative': 0.9044983523150818,
                        'uninformative': 0.0955016476849182
                    }
                ),
                (
                    'The CQ bit was checked by pkasting@chromium.org',
                    {
                        'informative': 0.013371042999968188,
                        'uninformative': 0.9866289570000318
                    }
                ),
                (
                    'Done.',
                    {
                        'informative': 0.9563228713934695,
                        'uninformative': 0.0436771286065305
                    }
                ),
                (
                    'Done.',
                    {
                        'informative': 0.9563228713934695,
                        'uninformative': 0.0436771286065305
                    }
                ),
                (
                    'policies.',
                    {
                        'informative': 0.9178244259879967,
                        'uninformative': 0.08217557401200326
                    }
                ),
                (
                    'are a copy of input flags.',
                    {
                        'informative': 0.13267751340537393,
                        'uninformative': 0.8673224865946261
                    }
                ),
                (
                    "Don't you think that it could make it more difficult",
                    {
                        'informative': 0.9765919663093432,
                        'uninformative': 0.023408033690656804
                    }
                ),
                (
                    'policy far from the DevTools creation?',
                    {
                        'informative': 0.9929333124240544,
                        'uninformative': 0.0070666875759456405
                    }
                ),
                (
                    'LGTM',
                    {
                        'informative': 0.8581510193910051,
                        'uninformative': 0.14184898060899487
                    }
                ),
                (
                    '+ pkasting@chromium.org',
                    {
                        'informative': 0.7410283395366474,
                        'uninformative': 0.2589716604633526
                    }
                ),
                (
                    'Code to disconnect the DevTools in kiosk mode.',
                    {
                        'informative': 0.014454731174187548,
                        'uninformative': 0.9855452688258125
                    }
                ),
                (
                    'frederic.jacob.78@gmail.com changed reviewers:',
                    {
                        'informative': 0.8620369326918487,
                        'uninformative': 0.13796306730815133
                    }
                ),
                (
                    'I removed the comment and merged the two conditions.',
                    {
                        'informative': 0.18404862421776477,
                        'uninformative': 0.8159513757822352
                    }
                ),
                (
                    'I though that it will fit in chrome/browser/prefs, but '
                    'all the policies',
                    {
                        'informative': 0.40187787296786126,
                        'uninformative': 0.5981221270321387
                    }
                ),
                (
                    'Did you have any place in mind where we can set the '
                    'policy?',
                    {
                        'informative': 0.9940663570595014,
                        'uninformative': 0.005933642940498585
                    }
                ),
                (
                    'pkasting@chromium.org changed reviewers:',
                    {
                        'informative': 0.850866489861351,
                        'uninformative': 0.14913351013864895
                    }
                ),
                (
                    'Nit: No blank line here',
                    {
                        'informative': 0.98278184552223,
                        'uninformative': 0.017218154477769976
                    }
                ),
                (
                    'to associate the disconnection of the Devtools with the '
                    'kiosk mode if we set this',
                    {
                        'informative': 0.006678405478473386,
                        'uninformative': 0.9933215945215266
                    }
                ),
                (
                    'Nit: Just combine this conditional with the one below.',
                    {
                        'informative': 0.2525347350009031,
                        'uninformative': 0.7474652649990969
                    }
                ),
                (
                    'I have put it there because it is the central place for '
                    'the Devtools creation and as such cover all possible case.',
                    {
                        'informative': 0.000113915393563202,
                        'uninformative': 0.9998860846064368
                    }
                ),
                (
                    'It work for all OS (Tested it on Win,Osx,Linux) and there '
                    'are already code to disable the Devtools at this place.',
                    {
                        'informative': 0.015033136641976799,
                        'uninformative': 0.9849668633580232
                    }
                ),
                (
                    'I would not try to set that pref in kiosk mode.',
                    {
                        'informative': 0.8270210951922724,
                        'uninformative': 0.1729789048077276
                    }
                ),
                (
                    'I looked all over the code and I did not saw any place '
                    'that looked good to set',
                    {
                        'informative': 0.8071936655298996,
                        'uninformative': 0.19280633447010043
                    }
                ),
                (
                    '+ dgozman@chromium.org, pkasting@google.com',
                    {
                        'informative': 0.16346179367164335,
                        'uninformative': 0.8365382063283566
                    }
                ),
                (
                    "You can probably nuke the comment on that since it's "
                    "just restating the code, rather than trying to expand it.",
                    {
                        'informative': 0.08000111107697262,
                        'uninformative': 0.9199988889230274
                    }
                ),
                (
                    'Is it possible to set the policy |prefs::kDevToolsDisabled'
                    '| instead in kiosk mode?',
                    {
                        'informative': 0.9663068414179109,
                        'uninformative': 0.0336931585820891
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
                        'informative': 0.000008741848515385136,
                        'uninformative': 0.9999912581514846
                    }
                )
            ]

        _ = self.tagger.tag()
        actual = Sentence.objects.filter(review_id=1259853004).values_list('text', 'metrics')
        actual = [(text, metrics['informativeness']) for text, metrics in actual]
        self.maxDiff = None

        e = sorted(expected, key=lambda x:x[0])
        a = sorted(actual, key=lambda x:x[0])
        for i, _ in enumerate(e):
            if e[i] != a[i]: # pragma: no cover
                print(e[i])
                print(a[i])
            self.assertEqual(e[i][0], a[i][0])
            self.assertDictEqual(e[i][1], a[i][1])
