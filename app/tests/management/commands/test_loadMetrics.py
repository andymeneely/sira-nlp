from django import test
from django.conf import settings

from app.models import *
from app.lib import loaders, helpers

from django.core.management import call_command


class LoadMetricsCommandTestCase(test.TransactionTestCase):
    def setUp(self):  # pragma: no cover
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

        sentObjects = Sentence.objects.filter(message__review_id=1259853004)

        self.expectedFormality = [
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
                    'the Devtools creation and as such cover all possible '
                    'case.',
                    {
                        'formal': 0.010657033433948061,
                        'informal': 0.9893429665660519
                    }
                ),
                (
                    'It work for all OS (Tested it on Win,Osx,Linux) and '
                    'there are already code to disable the Devtools at this '
                    'place.',
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
                    "just restating the code, rather than trying to expand "
                    "it.",
                    {
                        'formal': 0.9352595261512059,
                        'informal': 0.06474047384879411
                    }
                ),
                (
                    'Is it possible to set the policy '
                    '|prefs::kDevToolsDisabled| instead in kiosk mode?',
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
        self.expectedFormality = sorted(self.expectedFormality)
        self.expectedInformativeness = [
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
                    'the Devtools creation and as such cover all possible '
                    'case.',
                    {
                        'informative': 0.000113915393563202,
                        'uninformative': 0.9998860846064368
                    }
                ),
                (
                    'It work for all OS (Tested it on Win,Osx,Linux) and '
                    'there are already code to disable the Devtools at this '
                    'place.',
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
                    "just restating the code, rather than trying to expand "
                    "it.",
                    {
                        'informative': 0.08000111107697262,
                        'uninformative': 0.9199988889230274
                    }
                ),
                (
                    'Is it possible to set the policy '
                    '|prefs::kDevToolsDisabled| instead in kiosk mode?',
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
        self.expectedInformativeness = sorted(self.expectedInformativeness)
        self.expectedImplicature = [
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
        self.expectedImplicature = sorted(self.expectedImplicature)

    def test_no_args(self):
        self.assertRaises(Exception, call_command('loadMetrics'))

    def test_formality(self):
        call_command('loadMetrics', metrics=['formality'])

        actual = [
                (sentence.text, sentence.metrics['formality'])
                for sentence in Sentence.objects
                                        .filter(message__review_id=1259853004)
            ]
        actual = sorted(actual)
        for index in range(0, len(self.expectedFormality)):
            etext, emetrics = self.expectedFormality[index]
            atext, ametrics = actual[index]
            self.assertEqual(etext, atext)
            for metric in ['formal', 'informal']:
                self.assertAlmostEqual(
                        emetrics[metric], ametrics[metric],
                        msg='{}:{}'.format(metric, etext)
                    )

    def test_informativeness(self):
        call_command('loadMetrics', metrics=['informativeness'])

        actual = [
                (sentence.text, sentence.metrics['informativeness'])
                for sentence in Sentence.objects
                                        .filter(message__review_id=1259853004)
            ]
        actual = sorted(actual)
        for index in range(0, len(self.expectedInformativeness)):
            etext, emetrics = self.expectedInformativeness[index]
            atext, ametrics = actual[index]
            self.assertEqual(etext, atext)
            for metric in ['informative', 'uninformative']:
                self.assertAlmostEqual(
                        emetrics[metric], ametrics[metric],
                        msg='{}:{}'.format(metric, etext)
                    )

    def test_implicature(self):
        call_command('loadMetrics', metrics=['implicature'])

        actual = [
                (sentence.text, sentence.metrics['implicature'])
                for sentence in Sentence.objects
                                        .filter(message__review_id=1259853004)
            ]
        actual = sorted(actual)
        for index in range(0, len(self.expectedImplicature)):
            etext, emetrics = self.expectedImplicature[index]
            atext, ametrics = actual[index]
            self.assertEqual(etext, atext)
            for metric in ['implicative', 'unimplicative']:
                self.assertAlmostEqual(
                        emetrics[metric], ametrics[metric],
                        msg='{}:{}'.format(metric, etext)
                    )

    def test_multiple(self):
        call_command('loadMetrics', metrics=['formality', 'informativeness',
                                             'implicature'])
        actual = [
                (sentence.text, sentence.metrics['formality'])
                for sentence in Sentence.objects
                                        .filter(message__review_id=1259853004)
            ]
        actual = sorted(actual)
        for index in range(0, len(self.expectedFormality)):
            etext, emetrics = self.expectedFormality[index]
            atext, ametrics = actual[index]
            self.assertEqual(etext, atext)
            for metric in ['formal', 'informal']:
                self.assertAlmostEqual(
                        emetrics[metric], ametrics[metric],
                        msg='{}:{}'.format(metric, etext)
                    )

        actual = [
                (sentence.text, sentence.metrics['informativeness'])
                for sentence in Sentence.objects
                                        .filter(message__review_id=1259853004)
            ]
        actual = sorted(actual)
        for index in range(0, len(self.expectedInformativeness)):
            etext, emetrics = self.expectedInformativeness[index]
            atext, ametrics = actual[index]
            self.assertEqual(etext, atext)
            for metric in ['informative', 'uninformative']:
                self.assertAlmostEqual(
                        emetrics[metric], ametrics[metric],
                        msg='{}:{}'.format(metric, etext)
                    )

        actual = [
                (sentence.text, sentence.metrics['implicature'])
                for sentence in Sentence.objects
                                        .filter(message__review_id=1259853004)
            ]
        actual = sorted(actual)
        for index in range(0, len(self.expectedImplicature)):
            etext, emetrics = self.expectedImplicature[index]
            atext, ametrics = actual[index]
            self.assertEqual(etext, atext)
            for metric in ['implicative', 'unimplicative']:
                self.assertAlmostEqual(
                        emetrics[metric], ametrics[metric],
                        msg='{}:{}'.format(metric, etext)
                    )
