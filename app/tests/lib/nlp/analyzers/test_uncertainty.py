from collections import namedtuple
from unittest import TestCase

from app.lib.nlp import analyzers

Token = namedtuple('Token', ['token', 'stem', 'lemma', 'pos', 'chunk'])


class UncertaintyAnalyzerTestCase(TestCase):
    def setUp(self):
        pass

    def test_analyze(self):
        data = {
                'I am the walrus.': [
                    Token._make(['I', 'I', 'i', 'PRP', 'B-NP']),
                    Token._make(['am', 'am', 'be', 'VBP', 'B-VP']),
                    Token._make(['the', 'the', 'the', 'DT', 'B-NP']),
                    Token._make(['walrus', 'walru', 'walrus', 'NN', 'I-NP']),
                    Token._make(['.', '.', '.', '.', 'O'])
                ],
                'I am the eggman.': [
                    Token._make(['I', 'I', 'i', 'PRP', 'B-NP']),
                    Token._make(['am', 'am', 'be', 'VBP', 'B-VP']),
                    Token._make(['the', 'the', 'the', 'DT', 'B-NP']),
                    Token._make(['eggman', 'eggman', 'eggman', 'NN', 'I-NP']),
                    Token._make(['.', '.', '.', '.', 'O'])
                ],
                'Cells in Regulating Cellular Immunity': [
                    Token._make(['Cells', 'Cell', 'cells', 'NNS', 'B-NP']),
                    Token._make(['in', 'in', 'in', 'IN', 'B-PP']),
                    Token._make(
                        ['Regulating', 'Regul', 'regulating', 'VBG', 'B-VP']
                    ),
                    Token._make(
                        ['Cellular', 'Cellular', 'cellular', 'JJ', 'B-NP']
                    ),
                    Token._make(
                        ['Immunity', 'Immun', 'immunity', 'NN', 'I-NP']
                    )
                ]
            }
        expected = {
                'I am the walrus.': ['C', 'C', 'C', 'C', 'C'],
                'I am the eggman.': ['C', 'C', 'C', 'C', 'C'],
                'Cells in Regulating Cellular Immunity': [
                    'C', 'C', 'C', 'C', 'C'
                ]
            }
        actual = dict()
        for sentence, tokens in data.items():
            actual[sentence] = analyzers.UncertaintyAnalyzer(tokens).analyze()

        self.assertEqual(expected, actual)
