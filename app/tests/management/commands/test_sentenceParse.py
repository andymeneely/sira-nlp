from django.conf import settings
from django import test

from app.management.commands.sentenceParse import *

class SentenceParseCommandTestCase(test.TestCase):
    def setUp(self):
        pass

    def test_find_last_occurrence(self):
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
