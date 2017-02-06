from unittest import TestCase

from app.lib.nlp import preprocessor


class PreprocessorTestCase(TestCase):
    def setUp(self):
        pass

    def test_execute(self):
        data = (
                'Gulf Applied Technologies Inc said it sold its subsidiaries '
                'engaged in pipeline and terminal operations for 12.2 mln '
                'dlrs. The company said the sale is subject to certain post '
                'closing adjustments, which it did not explain. Reuter'
            )
        expected = [
                'gulf', 'applied', 'technologies', 'inc', 'say',
                'sell', 'subsidiary', 'engage', 'pipeline', 'terminal',
                'operation', '12.2', 'mln', 'dlrs', 'company', 'say', 'sale',
                'subject', 'certain', 'post', 'close', 'adjustment',
                'explain', 'reuter'
            ]
        actual = preprocessor.Preprocessor(data).execute()

        self.assertEqual(expected, actual)
