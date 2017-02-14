from unittest import TestCase

from app.lib.nlp import analyzers


class AnalyzerTestCase(TestCase):
    def setUp(self):
        self.analyzer = analyzers.Analyzer('')

    def test_analyze(self):
        self.assertRaises(NotImplementedError, self.analyzer.analyze)
