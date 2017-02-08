from unittest import TestCase

from app.lib.nlp.sentenizer import Sentenizer, NLTKSentenizer


class SentenizerTestCase(TestCase):
    def setUp(self):
        pass

    def test_Sentenizer(self):
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
            actual = Sentenizer(data).execute()

    def test_NLTKSentenizer(self):
        # Sub-Test 1
        data = (
                'Gulf Applied Technologies Inc said it sold its subsidiaries '
                'engaged in pipeline and terminal operations for 12.2 mln '
                'dlrs. The company said the sale is subject to certain post '
                'closing adjustments, which it did not explain. Reuter'
            )
        expected = [
                'Gulf Applied Technologies Inc said it sold its subsidiaries '
                'engaged in pipeline and terminal operations for 12.2 mln '
                'dlrs.', 'The company said the sale is subject to certain post '
                'closing adjustments, which it did not explain.', 'Reuter'
            ]

        actual = NLTKSentenizer(data).execute()

        self.assertEqual(expected, actual)

        # Sub-Test 2
        data = "I don't like that reviewers do not get the message."
        expected = [
                    "I don't like that reviewers do not get the message."
            ]

        actual = NLTKSentenizer(data).execute()

        self.assertEqual(expected, actual)

        # Sub-Test 3
        data = (
                "Can NLTK detect sentences that contain question marks? how "
                "about sentences that don't start with a capital letter? Or "
                "exclamations! Really excited statements!!! What does it do "
                "when you give it a mix of punctuation?!?!? Or elipses... "
                "And really bad! sentences that contain! punctuation in? bad "
                "places? . What about sentences that\nhave newlines in them?"
            )
        expected = [
                    "Can NLTK detect sentences that contain question marks?",
                    "how about sentences that don't start with a capital "
                    "letter?", "Or exclamations!", "Really excited "
                    "statements!!!", "What does it do when you give it a "
                    "mix of punctuation?!?!?", "Or elipses... And really "
                    "bad!", "sentences that contain!", "punctuation in?",
                    "bad places?", ".", "What about sentences that", "have "
                    "newlines in them?"
            ]

        actual = NLTKSentenizer(data).execute()

        self.assertEqual(expected, actual)
