from django import test
from django.conf import settings
from django.db import connection, connections
from django.db.models import Q

from app.lib import loaders, taggers
from app.models import *


class SentimentTestCase(test.TransactionTestCase):
    def setUp(self):
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

        connections.close_all()  # Hack

        q1 = Q(message__review_id=1259853004)
        q2 = Q(comment__patch__patchset__review_id=1259853004)
        sentObjects = Sentence.objects.filter(q1 | q2)
        self.tagger = taggers.SentimentTagger(
                settings, num_processes=2, sentObjects=sentObjects
            )

    def test_load(self):
        expected = [
                 (
                     'lgtm',
                     {'neg': 0, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 1}
                 ),
                 (
                     'Looks like you need LGTM from a devtools owner.',
                     {'neg': 0, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 1}
                 ),
                 (
                     'lgtm',
                     {'neg': 0, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 1}
                 ),
                 (
                     'I removed the comment and merged the two conditions.',
                     {'neg': 1, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 0}
                 ),
                 (
                     'Done.',
                     {'neg': 0, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 1}
                 ),
                 (
                     'Done.',
                     {'neg': 0, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 1}
                 ),
                 (
                     'I would not try to set that pref in kiosk mode.',
                     {'neg': 1, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 0}
                 ),
                 (
                     "There's no real win from doing so (we save one "
                     "conditional in one place but have to add code to set "
                     "the pref elsewhere) and it would make subsequent "
                     "non-kiosk runs still disable the dev tools unless we "
                     "added even more code to distinguish why the pref was "
                     "originally set and then unset it.",
                     {'neg': 0, 'pos': 0, 'vneg': 1, 'vpos': 0, 'neut': 0}
                 ),
                 (
                     'I looked all over the code and I did not saw any place '
                     'that looked good to set',
                     {'neg': 1, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 0}
                 ),
                 (
                     'policies.',
                     {'neg': 0, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 1}
                 ),
                 (
                     'I though that it will fit in chrome/browser/prefs, but '
                     'all the policies',
                     {'neg': 0, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 1}
                 ),
                 (
                     'are a copy of input flags.',
                     {'neg': 1, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 0}
                 ),
                 (
                     "Don't you think that it could make it more difficult",
                     {'neg': 1, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 0}
                 ),
                 (
                     'to associate the disconnection of the Devtools with the '
                     'kiosk mode if we set this',
                     {'neg': 0, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 1}
                 ),
                 (
                     'policy far from the DevTools creation?',
                     {'neg': 0, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 1}
                 ),
                 (
                     'Did you have any place in mind where we can set the '
                     'policy?',
                     {'neg': 1, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 0}
                 ),
                 (
                     'LGTM',
                     {'neg': 0, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 1}
                 ),
                 (
                     'Nit: No blank line here',
                     {'neg': 0, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 1}
                 ),
                 (
                     'Nit: Just combine this conditional with the one below.',
                     {'neg': 1, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 0}
                 ),
                 (
                     "You can probably nuke the comment on that since it's "
                     "just restating the code, rather than trying to expand "
                     "it.",
                     {'neg': 1, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 0}
                 ),
                 (
                     'Code to disconnect the DevTools in kiosk mode.',
                     {'neg': 1, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 0}
                 ),
                 (
                     'I have put it there because it is the central place for '
                     'the Devtools creation and as such cover all possible '
                     'case.',
                     {'neg': 1, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 0}
                 ),
                 (
                     'It work for all OS (Tested it on Win,Osx,Linux) and '
                     'there are already code to disable the Devtools at this '
                     'place.',
                     {'neg': 1, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 0}
                 ),
                 (
                     'Is it possible to set the policy '
                     '|prefs::kDevToolsDisabled| instead in kiosk mode?',
                     {'neg': 1, 'pos': 0, 'vneg': 0, 'vpos': 0, 'neut': 0}
                 ),
            ]

        _ = self.tagger.tag()

        q1 = Q(message__review_id=1259853004)
        q2 = Q(comment__patch__patchset__review_id=1259853004)
        actual = [
                (sentence.text, sentence.metrics['sentiment'])
                for sentence in Sentence.objects.filter(q1 | q2)
            ]
        self.assertCountEqual(expected, actual)
