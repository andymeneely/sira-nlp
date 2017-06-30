from django import test
from django.conf import settings
from django.db.models import Q

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
        loader = loaders.SentenceMessageLoader(
                settings, num_processes=2, review_ids=[1259853004]
            )
        _ = loader.load()
        loader = loaders.CommentLoader(
                settings, num_processes=2, review_ids=[1259853004]
            )
        _ = loader.load()
        loader = loaders.SentenceCommentLoader(
                settings, num_processes=2, review_ids=[1259853004]
            )
        _ = loader.load()
        loader = loaders.TokenLoader(
                settings, num_processes=2, review_ids=[1259853004]
            )
        _ = loader.load()

        q1 = Q(message__review_id=1259853004)
        q2 = Q(comment__patch__patchset__review_id=1259853004)
        self.sentObjects = Sentence.objects.filter(q1 | q2)

        self.expectedFormality = [
                ('Code to disconnect the DevTools in kiosk mode.', {'formal': 0.8133996729254985, 'informal': 0.18660032707450147}),
                ('Did you have any place in mind where we can set the policy?', {'formal': 0.9578748126664057, 'informal': 0.04212518733359427}),
                ("Don't you think that it could make it more difficult", {'formal': 0.9144682647190996, 'informal': 0.08553173528090041}),
                ('Done.', {'formal': 0.9560280075705169, 'informal': 0.04397199242948313}),
                ('Done.', {'formal': 0.9560280075705169, 'informal': 0.04397199242948313}),
                ('I have put it there because it is the central place for the Devtools creation and as such cover all possible case.', {'formal': 0.010657033433948061, 'informal': 0.9893429665660519}),
                ('I looked all over the code and I did not saw any place that looked good to set', {'formal': 0.9465330119933556, 'informal': 0.0534669880066444}),
                ('I removed the comment and merged the two conditions.', {'formal': 0.4907094516421489, 'informal': 0.5092905483578511}),
                ('I though that it will fit in chrome/browser/prefs, but all the policies', {'formal': 0.9639167742574419, 'informal': 0.03608322574255807}),
                ('I would not try to set that pref in kiosk mode.', {'formal': 0.9866015552582938, 'informal': 0.01339844474170615}),
                ('Is it possible to set the policy |prefs::kDevToolsDisabled| instead in kiosk mode?', {'formal': 0.9070844366402679, 'informal': 0.09291556335973206}),
                ('It work for all OS (Tested it on Win,Osx,Linux) and there are already code to disable the Devtools at this place.', {'formal': 0.9514776006037199, 'informal': 0.048522399396280114}),
                ('LGTM', {'formal': 0.9285427839666966, 'informal': 0.07145721603330335}), ('Looks like you need LGTM from a devtools owner.', {'formal': 0.7236392495196992, 'informal': 0.27636075048030084}),
                ('Nit: Just combine this conditional with the one below.', {'formal': 0.8324767352560595, 'informal': 0.16752326474394053}),
                ('Nit: No blank line here', {'formal': 0.9747818625399854, 'informal': 0.025218137460014556}),
                ("There's no real win from doing so (we save one conditional in one place but have to add code to set the pref elsewhere) and it would make subsequent non-kiosk runs still disable the dev tools unless we added even more code to distinguish why the pref was originally set and then unset it.", {'formal': 0.077391311892486, 'informal': 0.922608688107514}),
                ("You can probably nuke the comment on that since it's just restating the code, rather than trying to expand it.", {'formal': 0.9282941109660318, 'informal': 0.07170588903396824}),
                ('are a copy of input flags.', {'formal': 0.7587524581525787, 'informal': 0.24124754184742125}),
                ('lgtm', {'formal': 0.9554786484216474, 'informal': 0.044521351578352575}),
                ('lgtm', {'formal': 0.9554786484216474, 'informal': 0.044521351578352575}),
                ('policies.', {'formal': 0.8759002711822014, 'informal': 0.12409972881779863}),
                ('policy far from the DevTools creation?', {'formal': 0.8047949436225111, 'informal': 0.19520505637748886}),
                ('to associate the disconnection of the Devtools with the kiosk mode if we set this', {'formal': 0.9486603128100037, 'informal': 0.051339687189996264})
            ]
        self.expectedFormality = sorted(self.expectedFormality)
        self.expectedInformativeness = [
                ('Code to disconnect the DevTools in kiosk mode.', {'informative': 0.01928570933433253, 'uninformative': 0.9807142906656675}),
                ('Did you have any place in mind where we can set the policy?', {'informative': 0.9943710553240368, 'uninformative': 0.005628944675963199}),
                ("Don't you think that it could make it more difficult", {'informative': 0.9765919663093432, 'uninformative': 0.023408033690656804}),
                ('Done.', {'informative': 0.9584298402686305, 'uninformative': 0.04157015973136946}),
                ('Done.', {'informative': 0.9584298402686305, 'uninformative': 0.04157015973136946}),
                ('I have put it there because it is the central place for the Devtools creation and as such cover all possible case.', {'informative': 0.000113915393563202, 'uninformative': 0.9998860846064368}),
                ('I looked all over the code and I did not saw any place that looked good to set', {'informative': 0.8071936655298996, 'uninformative': 0.19280633447010043}),
                ('I removed the comment and merged the two conditions.', {'informative': 0.18404862421776477, 'uninformative': 0.8159513757822352}),
                ('I though that it will fit in chrome/browser/prefs, but all the policies', {'informative': 0.40187787296786126, 'uninformative': 0.5981221270321387}),
                ('I would not try to set that pref in kiosk mode.', {'informative': 0.8270210951922724, 'uninformative': 0.1729789048077276}),
                ('Is it possible to set the policy |prefs::kDevToolsDisabled| instead in kiosk mode?', {'informative': 0.9663068414179109, 'uninformative': 0.0336931585820891}),
                ('It work for all OS (Tested it on Win,Osx,Linux) and there are already code to disable the Devtools at this place.', {'informative': 0.01380055592148155, 'uninformative': 0.9861994440785185}),
                ('LGTM', {'informative': 0.8581510193910051, 'uninformative': 0.14184898060899487}),
                ('Looks like you need LGTM from a devtools owner.', {'informative': 0.0837672060862477, 'uninformative': 0.9162327939137523}),
                ('Nit: Just combine this conditional with the one below.', {'informative': 0.279843634053512, 'uninformative': 0.720156365946488}),
                ('Nit: No blank line here', {'informative': 0.98278184552223, 'uninformative': 0.017218154477769976}),
                ("There's no real win from doing so (we save one conditional in one place but have to add code to set the pref elsewhere) and it would make subsequent non-kiosk runs still disable the dev tools unless we added even more code to distinguish why the pref was originally set and then unset it.", {'informative': 1.0618471403402066e-05, 'uninformative': 0.9999893815285966}),
                ("You can probably nuke the comment on that since it's just restating the code, rather than trying to expand it.", {'informative': 0.09255934177647841, 'uninformative': 0.9074406582235216}),
                ('are a copy of input flags.', {'informative': 0.13267751340537393, 'uninformative': 0.8673224865946261}),
                ('lgtm', {'informative': 0.9044983523150818, 'uninformative': 0.0955016476849182}),
                ('lgtm', {'informative': 0.9044983523150818, 'uninformative': 0.0955016476849182}),
                ('policies.', {'informative': 0.9178244259879967, 'uninformative': 0.08217557401200326}),
                ('policy far from the DevTools creation?', {'informative': 0.9929333124240544, 'uninformative': 0.0070666875759456405}),
                ('to associate the disconnection of the Devtools with the kiosk mode if we set this', {'informative': 0.006678405478473386, 'uninformative': 0.9933215945215266})
            ]
        self.expectedInformativeness = sorted(self.expectedInformativeness)
        self.expectedImplicature = [
                ('Code to disconnect the DevTools in kiosk mode.', {'unimplicative': 0.16831943620263523, 'implicative': 0.8316805637973648}),
                ('Did you have any place in mind where we can set the policy?', {'unimplicative': 0.935002113821984, 'implicative': 0.06499788617801609}),
                ("Don't you think that it could make it more difficult", {'unimplicative': 0.9534186604863716, 'implicative': 0.04658133951362846}),
                ('Done.', {'unimplicative': 0.17913543741586524, 'implicative': 0.8208645625841348}),
                ('Done.', {'unimplicative': 0.17913543741586524, 'implicative': 0.8208645625841348}),
                ('I have put it there because it is the central place for the Devtools creation and as such cover all possible case.', {'unimplicative': 0.17943142822265745, 'implicative': 0.8205685717773425}),
                ('I looked all over the code and I did not saw any place that looked good to set', {'unimplicative': 0.9834895233648248, 'implicative': 0.0165104766351752}),
                ('I removed the comment and merged the two conditions.', {'unimplicative': 0.40866411018172843, 'implicative': 0.5913358898182716}),
                ('I though that it will fit in chrome/browser/prefs, but all the policies', {'unimplicative': 0.10484345154168517, 'implicative': 0.8951565484583148}),
                ('I would not try to set that pref in kiosk mode.', {'unimplicative': 0.8993074609313083, 'implicative': 0.1006925390686917}),
                ('Is it possible to set the policy |prefs::kDevToolsDisabled| instead in kiosk mode?', {'unimplicative': 0.6678448199566183, 'implicative': 0.3321551800433818}),
                ('It work for all OS (Tested it on Win,Osx,Linux) and there are already code to disable the Devtools at this place.', {'unimplicative': 0.5920308854330008, 'implicative': 0.4079691145669992}),
                ('LGTM', {'unimplicative': 0.2843028313513084, 'implicative': 0.7156971686486916}),
                ('Looks like you need LGTM from a devtools owner.', {'unimplicative': 0.5325648677846784, 'implicative': 0.4674351322153217}),
                ('Nit: Just combine this conditional with the one below.', {'unimplicative': 0.5137552416726234, 'implicative': 0.4862447583273765}),
                ('Nit: No blank line here', {'unimplicative': 0.7895862275605918, 'implicative': 0.21041377243940823}),
                ("There's no real win from doing so (we save one conditional in one place but have to add code to set the pref elsewhere) and it would make subsequent non-kiosk runs still disable the dev tools unless we added even more code to distinguish why the pref was originally set and then unset it.", {'unimplicative': 0.14697334727546862, 'implicative': 0.8530266527245314}),
                ("You can probably nuke the comment on that since it's just restating the code, rather than trying to expand it.", {'unimplicative': 0.917784039367348, 'implicative': 0.08221596063265199}),
                ('are a copy of input flags.', {'unimplicative': 0.5944975595371269, 'implicative': 0.40550244046287315}),
                ('lgtm', {'unimplicative': 0.2798707615220236, 'implicative': 0.7201292384779764}),
                ('lgtm', {'unimplicative': 0.2798707615220236, 'implicative': 0.7201292384779764}),
                ('policies.', {'unimplicative': 0.22278433058709457, 'implicative': 0.7772156694129054}),
                ('policy far from the DevTools creation?', {'unimplicative': 0.69174193094706, 'implicative': 0.30825806905293995}),
                ('to associate the disconnection of the Devtools with the kiosk mode if we set this', {'unimplicative': 0.40513914728341704, 'implicative': 0.594860852716583})
            ]
        self.expectedImplicature = sorted(self.expectedImplicature)

    def test_no_args(self):
        self.assertRaises(Exception, call_command('loadMetrics'))

    def test_loadMetrics(self):
        call_command('loadMetrics', metrics=['formality', 'informativeness',
                                             'implicature'])
        actual = [
                (sentence.text, sentence.metrics['formality'])
                for sentence in self.sentObjects
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
                for sentence in self.sentObjects
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
                for sentence in self.sentObjects
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
