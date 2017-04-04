from django import test
from django.conf import settings

from app.lib import loaders, taggers
from app.models import *

from django.core.management import call_command

class PolitenessTaggerTestCase(test.TransactionTestCase):
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
        self.tagger = taggers.PolitenessTagger(
                settings, num_processes=2, sentenceObjects=sentObjects
            )

    def test_load(self):
        call_command('sentenceParse')
        expected = [
                (
                    'The CQ bit was checked by pkasting@chromium.org',
                    {
                        'polite': 0.439007418522547,
                        'impolite': 0.5609925814774529
                    }
                ),
                (
                    'lgtm',
                    {
                        'polite': 0.439007418522547,
                        'impolite': 0.5609925814774529
                    }
                ),
                (
                    'lgtm',
                    {
                        'polite': 0.439007418522547,
                        'impolite': 0.5609925814774529
                    }
                ),
                (
                    'Looks like you need LGTM from a devtools owner.',
                    {
                        'polite': 0.43071451511946657,
                        'impolite': 0.5692854848805334
                    }
                ),
                (
                    'The CQ bit was checked by pkasting@chromium.org',
                    {
                        'polite': 0.439007418522547,
                        'impolite': 0.5609925814774529
                    }
                ),
                (
                    'Done.',
                    {
                        'polite': 0.439007418522547,
                        'impolite': 0.5609925814774529
                    }
                ),
                (
                    'Done.',
                    {
                        'polite': 0.439007418522547,
                        'impolite': 0.5609925814774529
                    }
                ),
                (
                    'policies.',
                    {
                        'polite': 0.439007418522547,
                        'impolite': 0.5609925814774529
                    }
                ),
                (
                    'policy far from the DevTools creation?',
                    {
                        'polite': 0.4523687007872979,
                        'impolite': 0.547631299212702
                    }
                ),
                (
                    'Did you have any place in mind where we can set the policy?',
                    {
                        'polite': 0.6248711449928428,
                        'impolite': 0.3751288550071572
                    }
                ),
                (
                    'LGTM',
                    {
                        'polite': 0.439007418522547,
                        'impolite': 0.5609925814774529
                    }
                ),
                (
                    'Nit: No blank line here',
                    {
                        'polite': 0.439007418522547,
                        'impolite': 0.5609925814774529
                    }
                ),
                (
                    'pkasting@chromium.org changed reviewers:',
                    {
                        'polite': 0.439007418522547,
                        'impolite': 0.5609925814774529
                    }
                ),
                (
                    '+ pkasting@chromium.org',
                    {
                        'polite': 0.439007418522547,
                        'impolite': 0.5609925814774529
                    }
                ),
                (
                    '+ dgozman@chromium.org, pkasting@google.com',
                    {
                        'polite': 0.439007418522547,
                        'impolite': 0.5609925814774529
                    }
                ),
                (
                    'are a copy of input flags.',
                    {
                        'polite': 0.439007418522547,
                        'impolite': 0.5609925814774529
                    }
                ),
                (
                    "Don't you think that it could make it more difficult",
                    {
                        'polite': 0.3137695942144514,
                        'impolite': 0.6862304057855485
                    }
                ),
                (
                    'I though that it will fit in chrome/browser/prefs, but all'
                    ' the policies',
                    {
                        'polite': 0.5258094349678502,
                        'impolite': 0.47419056503214996
                    }
                ),
                (
                    'Nit: Just combine this conditional with the one below.',
                    {
                        'polite': 0.4776029381549605,
                        'impolite': 0.5223970618450396
                    }
                ),
                (
                    'to associate the disconnection of the Devtools with the '
                    'kiosk mode if we set this',
                    {
                        'polite': 0.5069363847504353,
                        'impolite': 0.49306361524956466
                    }
                ),
                (
                    'frederic.jacob.78@gmail.com changed reviewers:',
                    {
                        'polite': 0.439007418522547,
                        'impolite': 0.5609925814774529
                    }
                ),
                (
                    'Code to disconnect the DevTools in kiosk mode.',
                    {
                        'polite': 0.439007418522547,
                        'impolite': 0.5609925814774529
                    }
                ),
                (
                    'I have put it there because it is the central place for '
                    'the Devtools creation and as such cover all possible case.',
                    {
                        'polite': 0.579824881138749,
                        'impolite': 0.42017511886125114
                    }
                ),
                (
                    'I would not try to set that pref in kiosk mode.',
                    {
                        'polite': 0.5734644886842811,
                        'impolite': 0.4265355113157188
                    }
                ),
                (
                    'I removed the comment and merged the two conditions.',
                    {
                        'polite': 0.4905052629887901,
                        'impolite': 0.5094947370112098
                    }
                ),
                (
                    'I looked all over the code and I did not saw any place '
                    'that looked good to set',
                    {
                        'polite': 0.5427824370789234,
                        'impolite': 0.4572175629210767
                    }
                ),
                (
                    "There's no real win from doing so (we save one conditional"
                    " in one place but have to add code to set the pref "
                    "elsewhere) and it would make subsequent non-kiosk runs "
                    "still disable the dev tools unless we added even more code"
                    " to distinguish why the pref was originally set and then "
                    "unset it.",
                    {
                        'polite': 0.5057137816218953,
                        'impolite': 0.4942862183781046
                    }
                ),
                (
                    'Is it possible to set the policy |prefs::kDevToolsDisabled'
                    '| instead in kiosk mode?',
                    {
                        'impolite': 0.41342652088375903,
                        'polite': 0.586573479116241
                    }
                ),
                (
                    "You can probably nuke the comment on that since it's just"
                    " restating the code, rather than trying to expand it.",
                    {
                        'polite': 0.45599157742251073,
                        'impolite': 0.5440084225774892
                    }
                ),
                (
                    'It work for all OS (Tested it on Win,Osx,Linux) and there'
                    ' are already code to disable the Devtools at this place.',
                    {'polite': 0.5, 'impolite': 0.5}
                )
            ]

        _ = self.tagger.tag()
        actual = Sentence.objects.filter(review_id=1259853004).values_list('text', 'metrics')
        actual = [(text, metrics['politeness']) for text, metrics in actual]
        self.maxDiff = None
        e = sorted(expected)
        a = sorted(actual)
        for i, _ in enumerate(e):
            self.assertEqual(e[i][0], a[i][0])
            self.assertDictEqual(e[i][1], a[i][1])
