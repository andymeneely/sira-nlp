from unittest import TestCase

from json import JSONDecodeError

from app.lib.nlp import analyzers


class ComplexityAnalyzerTestCase(TestCase):
    def setUp(self):
        pass

    def test_analyze(self):
        # Sub-Test 1
        data1 = ''
        data2 = ''

        expected = {'yngve': 0, 'frazier': 0, 'pdensity': 0, 'cdensity': 0}
        actual = analyzers.ComplexityAnalyzer(data1, data2).analyze()
        self.assertDictEqual(expected, actual)

        # Sub-Test 2
        data1 = 'Gulf Applied Technologies Inc said it sold its subsidiaries ' \
                'engaged in pipeline and terminal operations for 12.2 mln ' \
                'dlrs. '
        data2 = "( (S (NP (NNP Gulf) (NNP Applied) (NNPS Technologies) (NNP" \
                " Inc)) (VP (VBD said) (SBAR (S (NP (PRP it)) (VP (VBD sold)" \
                " (NP (NP (PRP$ its) (NNS subsidiaries)) (VP (VBN engaged) " \
                "(PP (IN in) (NP (NP (NN pipeline)) (CC and) (NP (JJ terminal)" \
                " (NNS operations)))) (PP (IN for) (NP (CD 12.2) (CD mln) " \
                "(NNS dlrs))))))))) (. .)))"

        expected = {'cdensity': 1.7142857142857142, 'frazier': 0.725, 'pdensity': 0.4, 'yngve': 2.55}
        actual = analyzers.ComplexityAnalyzer(data1, data2).analyze()
        self.assertDictEqual(expected, actual)
