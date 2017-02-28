from unittest import TestCase

from app.lib.nlp.lemmatizer import *

from nltk.corpus import wordnet

class LemmatizerTestCase(TestCase):
    def setUp(self):
        pass

    def test_Lemmatizer(self):
        # Sub-Test 1
        data = [
                'Gulf', 'Applied', 'Technologies', 'Inc', 'said', 'it', 'sold',
                'its', 'subsidiaries', 'engaged', 'in', 'pipeline', 'and',
                'terminal', 'operations', 'for', '12.2', 'mln', 'dlrs', '.',
                'The', 'company', 'said', 'the', 'sale', 'is', 'subject', 'to',
                'certain', 'post', 'closing', 'adjustments', ',', 'which',
                'it', 'did', 'not', 'explain', '.', 'Reuter'
            ]
        expected = [
                'gulf', 'applied', 'technologies', 'inc', 'say', 'it',
                'sell', 'its', 'subsidiary', 'engage', 'in', 'pipeline',
                'and', 'terminal', 'operation', 'for', '12.2', 'mln', 'dlrs',
                '.', 'the', 'company', 'say', 'the', 'sale', 'be', 'subject',
                'to', 'certain', 'post', 'closing', 'adjustment', ',', 'which',
                'it', 'do', 'not', 'explain', '.', 'reuter'
            ]

        with self.assertRaises(NotImplementedError):
            actual = Lemmatizer(data).execute()

    def test_NLTKLemmatizer(self):
        # Sub-Test 1
        data = [
                'Gulf', 'Applied', 'Technologies', 'Inc', 'said', 'it', 'sold',
                'its', 'subsidiaries', 'engaged', 'in', 'pipeline', 'and',
                'terminal', 'operations', 'for', '12.2', 'mln', 'dlrs', '.',
                'The', 'company', 'said', 'the', 'sale', 'is', 'subject', 'to',
                'certain', 'post', 'closing', 'adjustments', ',', 'which',
                'it', 'did', 'not', 'explain', '.', 'Reuter'
            ]
        expected = [
                'gulf', 'applied', 'technologies', 'inc', 'say', 'it',
                'sell', 'it', 'subsidiary', 'engage', 'in', 'pipeline',
                'and', 'terminal', 'operation', 'for', '12.2', 'mln', 'dlrs',
                '.', 'the', 'company', 'say', 'the', 'sale', 'be', 'subject',
                'to', 'certain', 'post', 'close', 'adjustment', ',', 'which',
                'it', 'do', 'not', 'explain', '.', 'reuter'
            ]

        actual = NLTKLemmatizer(data).execute()

        self.assertEqual(expected, actual)

        # Sub-Test 2
        data = [
                'I', 'do', 'n\'t', 'like', 'that', 'reviewers', 'do', 'not', 'get',
                'the', 'message', '.'
            ]
        expected = [
                    'i', 'do', 'not', 'like', 'that', 'reviewer', 'do', 'not',
                    'get', 'the', 'message', '.'
            ]

        actual = NLTKLemmatizer(data).execute()

        self.assertEqual(expected, actual)

        # Sub-Test 3
        expected = 'can'
        actual = fix('ca', "", None, ("n't", 'RB'))

        self.assertEqual(expected, actual)

        expected = ['as', 'long']
        actual = NLTKLemmatizer(['as', 'long']).execute()

        self.assertEqual(expected, actual)

        expected = ['who', 'be', 'leave']
        actual = NLTKLemmatizer(['who', 'is', 'left']).execute()

        self.assertEqual(expected, actual)

        expected = 'leave'
        actual = fix('left', 'left', ('is', wordnet.VERB), None)

        self.assertEqual(expected, actual)

        # Sub-Test 4
        expected = 'am'
        actual = fix("'m", "'m", ('I', wordnet.NOUN), None)

        self.assertEqual(expected, actual)

        expected = 'will'
        actual = fix("'ll", "'ll", ('I', wordnet.NOUN), None)

        self.assertEqual(expected, actual)

        expected = 'have'
        actual = fix("'ve", "'ve", ('I', wordnet.NOUN), None)

        self.assertEqual(expected, actual)

        expected = 'not'
        actual = fix("n't", "n't", ('ca', wordnet.VERB), None)

        self.assertEqual(expected, actual)

        expected = 'are'
        actual = fix("'re", "'re", ('they', wordnet.NOUN), None)

        self.assertEqual(expected, actual)
