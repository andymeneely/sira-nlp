from unittest import TestCase

from app.lib.nlp.tokenizer import NLTKTokenizer, Tokenizer


class TokenizerTestCase(TestCase):
    def setUp(self):
        pass

    def test_Tokenizer(self):
        # Sub-Test 1
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

        with self.assertRaises(NotImplementedError):
            actual = Tokenizer(data).execute()

    def test_NLTKTokenizer(self):
        # Sub-Test 1
        data = (
                'Gulf Applied Technologies Inc said it sold its subsidiaries '
                'engaged in pipeline and terminal operations for 12.2 mln '
                'dlrs. The company said the sale is subject to certain post '
                'closing adjustments, which it did not explain. Reuter'
            )
        expected = [
                'Gulf', 'Applied', 'Technologies', 'Inc', 'said', 'it',
                'sold', 'its', 'subsidiaries', 'engaged', 'in', 'pipeline',
                'and', 'terminal', 'operations', 'for', '12.2', 'mln', 'dlrs',
                '.', 'The', 'company', 'said', 'the', 'sale', 'is', 'subject',
                'to', 'certain', 'post', 'closing', 'adjustments', ',', 'which',
                'it', 'did', 'not', 'explain', '.', 'Reuter'
            ]

        actual = NLTKTokenizer(data).execute()

        self.assertEqual(expected, actual)

        # Sub-Test 2
        data = "I don't like that reviewers do not get the message."
        expected = [
                    'I', 'do', 'n\'t', 'like', 'that', 'reviewers', 'do', 'not',
                    'get', 'the', 'message', '.'
            ]

        actual = NLTKTokenizer(data).execute()

        self.assertEqual(expected, actual)
