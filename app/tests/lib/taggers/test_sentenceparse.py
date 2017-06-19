from django import test

from app.lib.taggers.sentenceparse import *
from app.lib.nlp.analyzers import SentenceParseAnalyzer

class SentenceparseTestCase(test.TestCase):
    def setUp(self):
        pass

    def test_sentenceparse(self):
        data = [
                'Gulf Applied Technologies Inc said it sold its subsidiaries '
                'engaged in pipeline and terminal operations for 12.2 mln '
                'dlrs. ',

                'The company said the sale is subject to certain post closing '
                'adjustments, which it did not explain. ',

                'Reuter'
            ]
        pass

    def test_helpers(self):
        self.maxDiff = None
        # Sub-Test 1
        data = (
                'Gulf Applied Technologies Inc said it sold its subsidiaries '
                'engaged in pipeline and terminal operations for 12.2 mln '
                'dlrs. '
            )

        expected = [
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
        actual = []
        parses = SentenceParseAnalyzer(data).analyze()
        for dep in parses['deps']:
            actual.append(clean_depparse(dep))

        self.assertListEqual(sorted(expected), sorted(actual))

        # Sub-Test 2
        expected = "( (S (NP (NNP Gulf) (NNP Applied) (NNPS Technologies) (NNP" \
                   " Inc)) (VP (VBD said) (SBAR (S (NP (PRP it)) (VP (VBD sold)" \
                   " (NP (NP (PRP$ its) (NNS subsidiaries)) (VP (VBN engaged) " \
                   "(PP (IN in) (NP (NP (NN pipeline)) (CC and) (NP (JJ terminal)" \
                   " (NNS operations)))) (PP (IN for) (NP (CD 12.2) (CD mln) " \
                   "(NNS dlrs))))))))) (. .)))"
        actual = clean_treeparse(parses['trees'])

        self.assertEqual(expected, actual)

        # Sub-Test 3
        data = (
               "The company said the sale is subject to certain post closing "
               "adjustments, which it did not explain."
           )
        expected = [
                'ROOT(root-0, said-3)', 'det(company-2, The-1)',
                'nsubj(said-3, company-2)', 'det(sale-5, the-4)',
                'nsubj(subject-7, sale-5)', 'cop(subject-7, is-6)',
                'ccomp(said-3, subject-7)', 'case(adjustments-12, to-8)',
                'amod(adjustments-12, certain-9)',
                'compound(adjustments-12, post-10)',
                'compound(adjustments-12, closing-11)',
                'nmod:to(subject-7, adjustments-12)',
                'dobj(explain-18, adjustments-12)', 'punct(adjustments-12, ,-13)',
                'ref(adjustments-12, which-14)', 'nsubj(explain-18, it-15)',
                'aux(explain-18, did-16)', 'neg(explain-18, not-17)',
                'acl:relcl(adjustments-12, explain-18)', 'punct(said-3, .-19)'
            ]
        actual = []
        parses = SentenceParseAnalyzer(data).analyze()
        for dep in parses['deps']:
            actual.append(clean_depparse(dep))

        self.assertListEqual(sorted(expected), sorted(actual))

        # Sub-Test 4
        expected = "( (S (NP (DT The) (NN company)) (VP (VBD said) (SBAR (S " \
                   "(NP (DT the) (NN sale)) (VP (VBZ is) (ADJP (JJ subject) " \
                   "(PP (TO to) (NP (NP (JJ certain) (NN post) (NN closing) " \
                   "(NNS adjustments)) (, ,) (SBAR (WHNP (WDT which)) (S (NP" \
                   " (PRP it)) (VP (VBD did) (RB not) (VP (VB explain)))))))" \
                   "))))) (. .)))"
        actual = clean_treeparse(parses['trees'])

        self.assertEqual(expected, actual)

        # Sub-Test 5
        data = ( "Reuter" )
        expected = ['ROOT(root-0, Reuter-1)']
        actual = []
        parses = SentenceParseAnalyzer(data).analyze()
        for dep in parses['deps']:
            actual.append(clean_depparse(dep))

        self.assertListEqual(sorted(expected), sorted(actual))

        # Sub-Test 6
        expected = "( (NP (NNP Reuter)))"
        actual = clean_treeparse(parses['trees'])

        self.assertEqual(expected, actual)

        # Sub-Test 7
        expected = "RegexFailed"
        actual = clean_treeparse([])
        self.assertEqual(expected, actual)

        # Sub-Test 8
        data = (
                "I.e., chromiumos_image.bin, chromiumos_image_base.bin, "
                "chromium_image_test.bin, etc."
            )
        expected = [
                'ROOT(root-0, bin-5)', 'advmod(bin-5, I.e.-1)',
                'punct(bin-5, ,-2)', 'dep(bin-5, chromiumos_image-3)',
                'punct(bin-5, .-4)', 'punct(bin-5, ,-6)',
                'compound(bin-9, chromiumos_image_base-7)',
                'punct(bin-9, .-8)', 'appos(bin-5, bin-9)',
                'punct(bin-9, ,-10)',
                'compound(bin-13, chromium_image_test-11)',
                'punct(bin-13, .-12)', 'conj(bin-9, bin-13)',
                'punct(bin-9, ,-14)', 'conj(bin-9, etc.-15)',
                'punct(bin-5, .-16)'
            ]
        actual = []
        parses = SentenceParseAnalyzer(data).analyze()
        for dep in parses['deps']:
            actual.append(clean_depparse(dep))
        self.assertListEqual(sorted(expected), sorted(actual))
