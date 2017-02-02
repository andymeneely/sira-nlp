"""
@AUTHOR: meyersbs
"""

from unittest import TestCase

from app.lib.nlp import tokenizer


class TokenizerTestCase(TestCase):
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
                'Gulf', 'Applied', 'Technologies', 'Inc', 'said', 'it', 'sold',
                'its', 'subsidiaries', 'engaged', 'in', 'pipeline', 'and',
                'terminal', 'operations', 'for', '12.2', 'mln', 'dlrs', '.',
                'The', 'company', 'said', 'the', 'sale', 'is', 'subject', 'to',
                'certain', 'post', 'closing', 'adjustments', ',', 'which',
                'it', 'did', 'not', 'explain', '.', 'Reuter'
            ]

        actual = tokenizer.Tokenizer(data).execute()

        self.assertEqual(expected, actual)

        data = "I don't like that reviewers do not get the message."
        expected = [
                'I', 'do', 'n\'t', 'like', 'that', 'reviewers', 'do', 'not',
                'get', 'the', 'message', '.'
            ]

        actual = tokenizer.Tokenizer(data).execute()

        self.assertEqual(expected, actual)
