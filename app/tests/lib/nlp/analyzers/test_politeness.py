from unittest import TestCase

from json import JSONDecodeError

from app.lib.nlp import analyzers

class PolitenessAnalyzerTestCase(TestCase):
    def setUp(self):
        pass

    def test_analyze(self):
        # Sub-Test 1
        data1 = ''
        data2 = ''

        expected = {'polite': 'EmptyText', 'impolite': 'EmptyText'}
        actual = analyzers.PolitenessAnalyzer(data1, data2).analyze()
        self.assertDictEqual(expected, actual)

        # Sub-Test 2
        data1 = 'Gulf Applied Technologies Inc said it sold its subsidiaries ' \
                'engaged in pipeline and terminal operations for 12.2 mln ' \
                'dlrs. '
        data2 = [
                'ROOT(root-0, said-5)', 'compound(inc-4, Gulf-1)',
                'compound(inc-4, Applied-2)', 'compound(inc-4, Technologies-3)',
                'nsubj(said-5, Inc-4)', 'nsubj(sold-7, it-6)',
                'ccomp(said-5, sold-7)', 'nmod:poss(subsidiaries-9, its-8)',
                'dobj(sold-7, subsidiaries-9)', 'acl(subsidiaries-9, engaged-10)',
                'case(pipeline-12, in-11)', 'nmod:in(engaged-10, pipeline-12)',
                'cc(pipeline-12, and-13)', 'amod(operations-15, terminal-14)',
                'nmod:in(engaged-10, operations-15)',
                'conj:and(pipeline-12, operations-15)', 'case(dlrs-19, for-16)',
                'compound(mln-18, 12.2-17)', 'nummod(dlrs-19, mln-18)',
                'nmod:for(sold-7, dlrs-19)', 'punct(said-5, .-20)'
            ]
        expected = {'impolite': 0.5609925814774529, 'polite': 0.43900741852254699}
        actual = analyzers.PolitenessAnalyzer(data1, data2).analyze()
        self.assertDictEqual(expected, actual)
