from django.conf import settings
from django.core.management import call_command
from django.db import transaction
from django.test import TransactionTestCase, override_settings
from django.utils.six import StringIO

from app.models import *
from app.lib import helpers
from app.queryStrings import *


from app.management.commands.sentenceParse import *

class SentenceParseCommandTestCase(TransactionTestCase):
    def setUp(self):
        pass

    def test_find_last_occurrence(self):
        # Sub-Test 1
        data = [
                'ROOT(root-0, said-5)', 'compound(inc-4, Gulf-1)',
                'compound(inc-4, Applied-2)', 'compound(inc-4, Technologies-3)',
                'nsubj(said-5, Inc-4)', 'nsubj(sold-7, it-6)',
                'ccomp(said-5, sold-7)', 'nmod:poss(subsidiaries-9, its-8)',
                'dobj(sold-7, subsidiaries-9)', 'acl(subsidiaries-9, engaged-10)',
                'case(pipeline-12, in-11)', 'nmod:in(engaged-10, pipeline-12)',
                'cc(pipeline-12, and-13)', 'amod(operations-15, terminal-14)',
                'ROOT(root-0, said-5)', 'nmod:in(engaged-10, operations-15)',
                'conj:and(pipeline-12, operations-15)', 'case(dlrs-19, for-16)',
                'compound(mln-18, 12.2-17)', 'nummod(dlrs-19, mln-18)',
                'nmod:for(sold-7, dlrs-19)', 'punct(said-5, .-20)'
           ]
        expected = 14
        actual = find_last_occurrence(data)
        self.assertEqual(expected, actual)

        # Sub-Test 2
        data = [
                'compound(inc-4, Gulf-1)', 'compound(inc-4, Applied-2)',
                'compound(inc-4, Technologies-3)', 'nsubj(said-5, Inc-4)',
                'nsubj(sold-7, it-6)', 'ccomp(said-5, sold-7)',
                'nmod:poss(subsidiaries-9, its-8)', 'dobj(sold-7, subsidiaries-9)',
                'acl(subsidiaries-9, engaged-10)', 'case(pipeline-12, in-11)',
                'nmod:in(engaged-10, pipeline-12)', 'cc(pipeline-12, and-13)',
                'amod(operations-15, terminal-14)',
                'nmod:in(engaged-10, operations-15)',
                'conj:and(pipeline-12, operations-15)', 'case(dlrs-19, for-16)',
                'compound(mln-18, 12.2-17)', 'nummod(dlrs-19, mln-18)',
                'nmod:for(sold-7, dlrs-19)', 'punct(said-5, .-20)'
           ]
        expected = -1
        actual = find_last_occurrence(data)
        self.assertEqual(expected, actual)


    def test_get_depparse(self):
        # Sub-Test 1
        data = ''
        expected = {'text': "", 'sentences': [], 'parses': [], 'score': 0.0}
        actual = get_depparse(data)
        self.assertEqual(expected, actual)

        # Sub-Test 2
        data = "Where did you learn English? How come you're taking on a third" \
               " language?"
        expected = {
                'text': "Where did you learn English? How come you're taking"
                        " on a third language?",
                'sentences': [
                                 'Where did you learn English?',
                                 "How come you're taking on a third language?"
                             ],
                'parses': [
                              [
                                  'ROOT(root-0, learn-4)',
                                  'advmod(learn-4, Where-1)',
                                  'aux(learn-4, did-2)',
                                  'nsubj(learn-4, you-3)',
                                  'xcomp(learn-4, English-5)',
                                  'punct(learn-4, ?-6)'
                              ],
                              [
                                  'ROOT(root-0, come-2)',
                                  'advmod(come-2, How-1)',
                                  'nsubj(taking-5, you-3)',
                                  "aux(taking-5, 're-4)",
                                  'ccomp(come-2, taking-5)',
                                  'case(language-9, on-6)',
                                  'det(language-9, a-7)',
                                  'amod(language-9, third-8)',
                                  'nmod:on(taking-5, language-9)',
                                  'punct(come-2, ?-10)'
                              ]
                          ],
                'score': 0.0
            }
        actual = get_depparse(data)
        self.assertDictEqual(expected, actual)
