from unittest import TestCase

from app.lib.nlp import tokenremover


class StopWordsRemoverTestCase(TestCase):
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
                'Gulf', 'Applied', 'Technologies', 'Inc', 'said', 'sold',
                'subsidiaries', 'engaged', 'pipeline', 'terminal',
                'operations', '12.2', 'mln', 'dlrs', '.', 'company',
                'said', 'sale', 'subject', 'certain', 'post', 'closing',
                'adjustments', ',', 'explain', '.', 'Reuter'
            ]

        actual = tokenremover.TokenRemover(data, filters=['SW']).execute()

        self.assertEqual(expected, actual)

        data = [
                'Stop', 'word', 'removal', 'MUST', 'BE', 'case-insensitive',
                '.'
            ]
        expected = ['Stop', 'word', 'removal', 'MUST', 'case-insensitive', '.']

        actual = tokenremover.TokenRemover(data, filters=['SW']).execute()

        self.assertEqual(expected, actual)

        data = [
                'The', 'sentence', 'will', ',', 'if', 'the', 'code', 'works',
                'as', 'expected', ',', 'be', 'void', 'of', 'any', 'stop',
                'words', 'and', 'punctuations', '.', 'Is', 'n\'t', 'that',
                'cool', '?'
            ]
        expected = [
                'sentence', 'code', 'works', 'expected', 'void', 'stop',
                'words', 'punctuations', 'n\'t', 'cool'
            ]

        actual = tokenremover.TokenRemover(data).execute()

        self.assertEqual(expected, actual)

        with self.assertRaises(Exception, msg='ZZ is an unknown filter'):
            _ = tokenremover.TokenRemover(data, filters=['ZZ'])
