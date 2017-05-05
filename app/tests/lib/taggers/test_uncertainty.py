import pprint

from django import test
from django.conf import settings

from app.lib import loaders, taggers
from app.models import *

from django.core.management import call_command

PRINTER = pprint.PrettyPrinter(indent=4, width=80)

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
        self.tagger = taggers.UncertaintyTagger(
                settings, num_processes=2, sentenceObjects=sentObjects
            )

    def test_load(self):
        call_command('sentenceParse')
        expected = [
                     ( 'lgtm', { 'SENTENCE': 'c', 'lgtm': 'c' } ),
                     ( 'lgtm', { 'SENTENCE': 'c', 'lgtm': 'c' } ),
                     ( 'The CQ bit was checked by pkasting@chromium.org',
                       { 'CQ': 'c', 'SENTENCE': 'c', 'The': 'c', 'bit': 'c',
                         'by': 'c', 'checked': 'c',
                         'pkasting@chromium.org': 'c', 'was': 'c' } ),
                     ( 'I removed the comment and merged the two conditions.',
                       { 'I': 'c', 'SENTENCE': 'c', 'and': 'c', 'merged': 'c',
                         'comment': 'c', 'conditions.': 'c', 'removed': 'c',
                         'the': 'c', 'two': 'c' } ),
                     ( 'Done.', { 'Done.': 'c', 'SENTENCE': 'c' } ),
                     ( 'Done.', { 'Done.': 'c', 'SENTENCE': 'c' } ),
                     ( 'policies.', { 'SENTENCE': 'c', 'policies.': 'c' } ),
                     ( 'are a copy of input flags.', { 'SENTENCE': 'c',
                         'a': 'c', 'are': 'c', 'copy': 'c', 'flags.': 'c',
                         'input': 'c', 'of': 'c' } ),
                     ( 'policy far from the DevTools creation?', { 'far': 'c',
                         'DevTools': 'c', 'SENTENCE': 'c', 'creation?': 'c',
                         'from': 'c', 'policy': 'c', 'the': 'c' } ),
                     ( 'LGTM', { 'LGTM': 'c', 'SENTENCE': 'c' } ),
                     ( 'Nit: No blank line here', { 'Nit:': 'c', 'No': 'c',
                         'SENTENCE': 'c', 'blank': 'c', 'here': 'c',
                         'line': 'c' } ),
                     ( 'pkasting@chromium.org changed reviewers:',
                       { 'SENTENCE': 'c', 'changed': 'c', 'reviewers:': 'c',
                         'pkasting@chromium.org': 'c' } ),
                     ( '+ pkasting@chromium.org', { '+': 'c', 'SENTENCE': 'c',
                         'pkasting@chromium.org': 'c' } ),
                     ( 'frederic.jacob.78@gmail.com changed reviewers:',
                       { 'SENTENCE': 'c', 'changed': 'c', 'reviewers:': 'c',
                         'frederic.jacob.78@gmail.com': 'c' } ),
                     ( '+ dgozman@chromium.org, pkasting@google.com',
                       { '+': 'c', 'dgozman@chromium.org,': 'c',
                         'SENTENCE': 'c', 'pkasting@google.com': 'c' } ),
                     ( 'Did you have any place in mind where we can set the '
                       'policy?', { 'Did': 'c', 'SENTENCE': 'c', 'any': 'c',
                         'can': 'c', 'have': 'c', 'in': 'c', 'mind': 'c',
                         'place': 'c', 'policy?': 'c', 'set': 'c', 'the': 'c',
                         'we': 'c', 'where': 'c', 'you': 'c' } ),
                     ( 'Nit: Just combine this conditional with the one '
                       'below.', { 'Just': 'c', 'Nit:': 'c', 'SENTENCE': 'c',
                         'below.': 'c', 'combine': 'c', 'conditional': 'c',
                         'one': 'c', 'the': 'c', 'this': 'c', 'with': 'c' } ),
                     ( 'Is it possible to set the policy |prefs::kDevToolsDi'
                       'sabled| instead in kiosk mode?',
                         { 'ERROR': "<class 'ValueError'>" } ),
                     ( 'Code to disconnect the DevTools in kiosk mode.',
                       { 'Code': 'c', 'DevTools': 'c', 'SENTENCE': 'c',
                         'disconnect': 'c', 'in': 'c', 'kiosk': 'c',
                         'mode.': 'c', 'the': 'c', 'to': 'c' } ),
                     ( 'The CQ bit was checked by pkasting@chromium.org',
                       { 'CQ': 'c', 'SENTENCE': 'c', 'The': 'c', 'bit': 'c',
                         'by': 'c', 'checked': 'c', 'was': 'c',
                         'pkasting@chromium.org': 'c' } ),
                     ( "There's no real win from doing so (we save one "
                       "conditional in one place but have to add code to set "
                       "the pref elsewhere) and it would make subsequent "
                       "non-kiosk runs still disable the dev tools unless we "
                       "added even more code to distinguish why the pref was "
                       "originally set and then unset it.", { '(we': 'c',
                         'SENTENCE': 'c', "There's": 'c', 'add': 'c',
                         'added': 'c', 'and': 'c', 'but': 'c', 'code': 'c',
                         'conditional': 'c', 'dev': 'c', 'disable': 'c',
                         'distinguish': 'c', 'doing': 'c', 'elsewhere)': 'c',
                         'even': 'c', 'from': 'c', 'have': 'c', 'in': 'c',
                         'it': 'c', 'it.': 'c', 'make': 'c', 'more': 'c',
                         'no': 'c', 'non-kiosk': 'c', 'one': 'c', 'pref': 'c',
                         'originally': 'c', 'place': 'c', 'subsequent': 'c',
                         'real': 'c', 'runs': 'c', 'save': 'c', 'set': 'c',
                         'so': 'c', 'still': 'c', 'the': 'c', 'then': 'c',
                         'to': 'c', 'tools': 'c', 'unless': 'c', 'unset': 'c',
                         'was': 'c', 'we': 'c', 'why': 'c', 'win': 'c',
                         'would': 'c' } ),
                     ( 'I would not try to set that pref in kiosk mode.',
                       { 'I': 'c', 'SENTENCE': 'u', 'in': 'c', 'kiosk': 'c',
                         'mode.': 'c', 'not': 'c', 'pref': 'c', 'set': 'c',
                         'that': 'c', 'to': 'c', 'try': 'c', 'would': 'u' } ),
                     ( 'Looks like you need LGTM from a devtools owner.',
                       { 'LGTM': 'c', 'Looks': 'c', 'SENTENCE': 'c',
                         'a': 'c', 'devtools': 'c', 'from': 'c', 'like': 'c',
                         'need': 'c', 'owner.': 'c', 'you': 'c' } ),
                     ( 'I looked all over the code and I did not saw any '
                       'place that looked good to set', { 'I': 'c', 'to': 'c',
                         'SENTENCE': 'c', 'all': 'c', 'and': 'c', 'any': 'c',
                         'code': 'c', 'did': 'c', 'good': 'c', 'looked': 'c',
                         'not': 'c', 'over': 'c', 'place': 'c', 'saw': 'c',
                         'set': 'c', 'that': 'c', 'the': 'c' } ),
                     ( "Don't you think that it could make it more difficult",
                       { "Don't": 'c', 'SENTENCE': 'c', 'could': 'c',
                         'difficult': 'c', 'it': 'c', 'make': 'c', 'you': 'c',
                         'more': 'c', 'that': 'c', 'think': 'c' } ),
                     ( 'to associate the disconnection of the Devtools with '
                       'the kiosk mode if we set this', { 'Devtools': 'c',
                         'SENTENCE': 'u', 'associate': 'c', 'kiosk': 'c',
                         'disconnection': 'c', 'if': 'u', 'mode': 'c',
                         'of': 'c', 'set': 'c', 'the': 'c', 'this': 'c',
                         'to': 'c', 'we': 'c', 'with': 'c' } ),
                     ( 'I though that it will fit in chrome/browser/prefs, '
                       'but all the policies', { 'I': 'c', 'SENTENCE': 'c',
                         'all': 'c', 'but': 'c', 'chrome/browser/prefs,': 'c',
                         'fit': 'c', 'in': 'c', 'it': 'c', 'policies': 'c',
                         'that': 'c', 'the': 'c', 'though': 'c', 'will': 'c' } ),
                     ( "You can probably nuke the comment on that since it's"
                       " just restating the code, rather than trying to "
                       "expand it.", { 'SENTENCE': 'u', 'You': 'c', 'to': 'c',
                         'can': 'c', 'code,': 'c', 'comment': 'c', 'it.': 'c',
                         'expand': 'c', "it's": 'c', 'just': 'c', 'nuke': 'c',
                         'probably': 'u', 'rather': 'c', 'restating': 'c',
                         'since': 'c', 'on': 'c', 'than': 'c', 'that': 'c',
                         'the': 'c', 'trying': 'c' } ),
                     ( 'I have put it there because it is the central place '
                       'for the Devtools creation and as such cover all '
                       'possible case.', { 'Devtools': 'c', 'possible': 'u',
                         'SENTENCE': 'u', 'all': 'c', 'and': 'c', 'as': 'c',
                         'because': 'c', 'case.': 'c', 'central': 'c',
                         'cover': 'c', 'creation': 'c', 'for': 'c', 'it': 'c',
                         'have': 'c', 'is': 'c', 'place': 'c', 'there': 'c',
                         'put': 'c', 'such': 'c', 'the': 'c', 'I': 'c' } ),
                     ( 'It work for all OS (Tested it on Win,Osx,Linux) and '
                       'there are already code to disable the Devtools at '
                       'this place.', { '(Tested': 'c', 'Devtools': 'c',
                         'It': 'c', 'OS': 'c', 'SENTENCE': 'c', 'place.': 'c',
                         'Win,Osx,Linux)': 'c', 'all': 'c', 'already': 'c',
                         'and': 'c', 'are': 'c', 'at': 'c', 'code': 'c',
                         'disable': 'c', 'for': 'c', 'it': 'c', 'on': 'c',
                         'the': 'c', 'there': 'c', 'this': 'c', 'to': 'c',
                         'work': 'c' } )
                   ]
        _ = self.tagger.tag()
        actual = Sentence.objects.filter(review_id=1259853004).values_list('text', 'metrics')
        actual = [(text, metrics['uncertainty']) for text, metrics in actual]
#        PRINTER.pprint(actual)
        self.maxDiff = None
        e = sorted(expected)
        a = sorted(actual)
        for i, _ in enumerate(e):
            self.assertEqual(e[i][0], a[i][0])
            self.assertDictEqual(e[i][1], a[i][1])
