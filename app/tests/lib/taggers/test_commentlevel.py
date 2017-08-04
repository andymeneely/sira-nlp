from django import test
from django.conf import settings
from django.db import connections
from django.db.models import Q

from app.lib import loaders, taggers
from app.models import *

from django.core.management import call_command


class CommentLevelTaggerTestCase(test.TransactionTestCase):
    def setUp(self):
        loader = loaders.ReviewLoader(settings, num_processes=2)
        _ = loader.load()
        loader = loaders.MessageLoader(
                settings, num_processes=2, review_ids=[1318783003]
            )
        _ = loader.load()
        loader = loaders.SentenceMessageLoader(
                settings, num_processes=2, review_ids=[1318783003]
            )
        _ = loader.load()
        loader = loaders.CommentLoader(
                settings, num_processes=2, review_ids=[1318783003]
            )
        _ = loader.load()
        loader = loaders.SentenceCommentLoader(
                settings, num_processes=2, review_ids=[1318783003]
            )
        _ = loader.load()

        q1 = Q(message__review_id=1318783003)
        q2 = Q(comment__patch__patchset__review_id=1318783003)
        sentObjects = Sentence.objects.filter(q1 | q2)

        tagger = taggers.SentenceParseTagger(
                settings, num_processes=2, sentences=sentObjects
            )
        _ = tagger.tag()

        connections.close_all()  # Hack

#        commObjects = Comment.objects.filter(patch__patchset__review_id=1259853004)
        commObjects = Comment.objects.all()

        self.tagger = taggers.CommentLevelTagger(
                settings, num_processes=2, commObjects=commObjects
            )

    def test_load(self):
        expected = [
                ('\nDone.', 0),
                ('\nDone.', 0),
                ('\nDone.', 0),
                ('\nDone.', 0),
                ("\nI can do that, with an extra check (we can only return othe"
                 "r if it's indeed is a string).", 1.0),
                ('Can we keep the fast loop that combines in 32-bit chunks at a'
                 ' time? Then we need to deal with the remaining 1, 2 or 3 byte'
                 's at the end. We can then do those one byte at a time?',
                 0.7391304347826086),
                ('I think we can share the implementation of length and just ha'
                 've a StringLength native? Lenght is from BaseArray I think, s'
                 'o it should be fine to just assert that the argument is a One'
                 'ByteString or a TwoByteString and then return BaseArray::cast'
                 '(object)->length()?', 1.4210526315789473),
                ('Lift the length checks on x out?\n\nint xlen = x->lenght();\n'
                 'if (xlen == 0) return other;\n\nand then remove it in the two'
                 ' branches?\n\nI think you can do the length computation as we'
                 'll since you know they are both BaseArrays and that is where '
                 'you get the length from.', 1.12),
                ('Same comments about length computations.', 4.0),
                ('o -> object', 0)
            ]
        expected = sorted(expected)

        _ = self.tagger.tag()

        actual = [
                (comment.text, comment.metrics['complexity']['cdensity'])
                for comment in Comment.objects.filter(patch__patchset__review_id=1318783003)
            ]

        actual = sorted(actual)
        for i, e in enumerate(expected):
            self.assertCountEqual(e, actual[i])
