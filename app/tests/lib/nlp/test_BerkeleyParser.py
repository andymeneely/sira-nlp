from unittest import TestCase

from app.lib.nlp.BerkeleyParser import *

from app.lib.logger import *

class BerkeleyParserTestCase(TestCase):
    def setUp(self):
        pass

    def test_BerkeleyParser(self):
        parser = BerkeleyParser()

        self.assertRaises(ValueError, parser.parse, 8.3)
        self.assertRaises(ValueError, parser.parse, 15)
        self.assertRaises(ValueError, parser.parse, parser)

        data = ['I am the walrus.', 'I am the eggman.']
        expected = ['( (S (NP (PRP I)) (VP (VBP am) (NP (DT the) (NN walrus.)))'
                    ') )', '( (S (NP (PRP I)) (VP (VBP am) (NP (DT the) (NN egg'
                    'man.)))) )']
        actual = parser.parse(data)
        self.assertEqual(expected, actual)

        data = [['I am the walrus.'], ['I am the eggman.']]
        expected = []
        actual = parser.parse(data)
        self.assertEqual(expected, actual)

        lg = logger
        expected = 'Deactivating the Berkeley Parser...'
        result = parser.deactivate(lg=lg)
        actual = lg.get_last_log()
        self.assertEqual(expected, actual)
