from unittest import TestCase

from app.lib.nlp.complexity import *
from nltk.tree import Tree

from app.lib import logger

class ComplexityTestCase(TestCase):
    def setUp(self):
        pass

    def test_get_mean_yngve(self):
        sent = "Colorless green ideas sleep furiously"
        parse = ['( (S (NP (NNP Colorless) (JJ green) (NNS ideas)) (VP (VBP sleep) (ADVP (RB furiously)))) )']

        expected = 1.4
        actual = get_mean_yngve(parse)
        self.assertEqual(expected, actual)

        sent = ''
        parse = ['()']

        expected = 0.0
        actual = get_mean_yngve(parse)
        self.assertEqual(expected, actual)

        self.assertRaises(ValueError, get_mean_yngve, [''])
        self.assertRaises(ValueError, get_mean_yngve, 0.0)

    def test_yngve_redux(self):
        sent = "Colorless green ideas sleep furiously"
        parse = ['( (S (NP (NNP Colorless) (JJ green) (NNS ideas)) (VP (VBP sleep) (ADVP (RB furiously)))) )']

        expected = [7.0, 5.0]
        actual = yngve_redux(parse[0])
        self.assertEqual(expected, actual)

    def test_calc_yngve_score(self):
        sent = "Colorless green ideas sleep furiously"
        parse = ['( (S (NP (NNP Colorless) (JJ green) (NNS ideas)) (VP (VBP sleep) (ADVP (RB furiously)))) )']

        expected = 7
        actual = calc_yngve_score(Tree.fromstring(parse[0]), 0)
        self.assertEqual(expected, actual)

    def test_get_mean_frazier(self):
        sent = "Colorless green ideas sleep furiously"
        parse = ['( (S (NP (NNP Colorless) (JJ green) (NNS ideas)) (VP (VBP sleep) (ADVP (RB furiously)))) )']

        expected = 0.9
        actual = get_mean_frazier(parse)
        self.assertEqual(expected, actual)

        sent = ''
        parse = ['()']

        expected = 0.0
        actual = get_mean_frazier(parse)
        self.assertEqual(expected, actual)

        expected = 'ZeroDivisionError for Frazier calculation.'
        lg = logger
        result = get_mean_frazier(parse, lg=lg)
        actual = lg.get_last_log()
        self.assertEqual(expected, actual)
        self.assertEqual(0.0, result)

        with self.assertRaises(ValueError):
            get_mean_frazier([''])
            get_mean_frazier(0.0)

    def test_calc_frazier_score(self):
        sent = "Colorless green ideas sleep furiously"
        parse = ['( (S (NP (NNP Colorless) (JJ green) (NNS ideas)) (VP (VBP sleep) (ADVP (RB furiously)))) )']

        expected = 4.5
        actual = calc_frazier_score(Tree.fromstring(parse[0]), 0, '')
        self.assertEqual(expected, actual)

        expected = -1
        actual = calc_frazier_score("Hi!", 0, '')
        self.assertEqual(expected, actual)
