from unittest import TestCase

from json import JSONDecodeError

from app.lib.nlp import analyzers

class UncertaintyAnalyzerTestCase(TestCase):
    def setUp(self):
        pass

    def test_analyze(self):
        # Sub-Test 1
        expected = {"sent": 'X', "words": []}
        actual = analyzers.UncertaintyAnalyzer("").analyze()
        self.assertDictEqual(expected, actual)

        # Sub-Test 2
        data = [
                  "I am the walrus.", "I am the eggman.",
                  "Cells in Regulating Cellular Immunity"
            ]
        expected = [
                {'sent': 'C', 'words': ['C', 'C', 'C', 'C']},
                {'sent': 'C', 'words': ['C', 'C', 'C', 'C']},
                {'sent': 'C', 'words': ['C', 'C', 'C', 'C', 'C']}
            ]
        for i, item in enumerate(data):
            exp = expected[i]
            actual = analyzers.UncertaintyAnalyzer(item).analyze()
            self.assertDictEqual(exp, actual)
