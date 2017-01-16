from unittest import TestCase

from app.lib.nlp import stemmer


class StemmerTestCase(TestCase):
    def setUp(self):
        pass

    def test_execute(self):
        data = [
                'Gulf', 'Applied', 'Technologies', 'Inc', 'said', 'it', 'sold',
                'its', 'subsidiaries', 'engaged', 'in', 'pipeline', 'and',
                'terminal', 'operations', 'for', '12.2', 'mln', 'dlrs', '.',
                'The', 'company', 'said', 'the', 'sale', 'is', 'subject', 'to',
                'certain', 'post', 'closing', 'adjustments', ',', 'which',
                'it', 'did', 'not', 'explain', '.', 'Reuter'
            ]
        expected = [
                'Gulf', 'Appli', 'Technolog', 'Inc', 'said', 'it', 'sold',
                'it', 'subsidiari', 'engag', 'in', 'pipelin', 'and', 'termin',
                'oper', 'for', '12.2', 'mln', 'dlr', '.', 'The', 'compani',
                'said', 'the', 'sale', 'is', 'subject', 'to', 'certain',
                'post', 'close', 'adjust', ',', 'which', 'it', 'did', 'not',
                'explain', '.', 'Reuter'
            ]

        actual = stemmer.Stemmer(data).execute()

        self.assertEqual(expected, actual)
