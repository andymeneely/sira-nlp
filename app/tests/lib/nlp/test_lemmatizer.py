from unittest import TestCase

from app.lib.nlp import lemmatizer


class LemmatizerTestCase(TestCase):
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
                'gulf', 'applied', 'technologies', 'inc', 'say', 'it',
                'sell', 'its', 'subsidiary', 'engage', 'in', 'pipeline',
                'and', 'terminal', 'operation', 'for', '12.2', 'mln', 'dlrs',
                '.', 'the', 'company', 'say', 'the', 'sale', 'be', 'subject',
                'to', 'certain', 'post', 'closing', 'adjustment', ',', 'which',
                'it', 'do', 'not', 'explain', '.', 'reuter'
            ]

        actual = lemmatizer.Lemmatizer(data).execute()

        self.assertEqual(expected, actual)
