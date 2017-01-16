from unittest import TestCase

from app.lib.nlp import stopwordsremover


class StopWordsRemoverTestCase(TestCase):
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
                'Gulf', 'Applied', 'Technologies', 'Inc', 'said', 'sold',
                'subsidiaries', 'engaged', 'pipeline', 'terminal',
                'operations', '12.2', 'mln', 'dlrs', '.', 'The', 'company',
                'said', 'sale', 'subject', 'certain', 'post', 'closing',
                'adjustments', ',', 'explain', '.', 'Reuter'
            ]

        actual = stopwordsremover.StopWordsRemover(data).execute()

        self.assertEqual(expected, actual)
