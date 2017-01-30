from unittest import TestCase

from app.lib.nlp import postagger


class PosTaggerTestCase(TestCase):
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
                ('Gulf', 'NNP'), ('Applied', 'NNP'), ('Technologies', 'NNPS'),
                ('Inc', 'NNP'), ('said', 'VBD'), ('it', 'PRP'),
                ('sold', 'VBD'), ('its', 'PRP$'), ('subsidiaries', 'NNS'),
                ('engaged', 'VBN'), ('in', 'IN'), ('pipeline', 'NN'),
                ('and', 'CC'), ('terminal', 'JJ'), ('operations', 'NNS'),
                ('for', 'IN'), ('12.2', 'CD'), ('mln', 'NN'), ('dlrs', 'NN'),
                ('.', '.'), ('The', 'DT'), ('company', 'NN'), ('said', 'VBD'),
                ('the', 'DT'), ('sale', 'NN'), ('is', 'VBZ'),
                ('subject', 'JJ'), ('to', 'TO'), ('certain', 'JJ'),
                ('post', 'NN'), ('closing', 'NN'), ('adjustments', 'NNS'),
                (',', ','), ('which', 'WDT'), ('it', 'PRP'), ('did', 'VBD'),
                ('not', 'RB'), ('explain', 'VB'), ('.', '.'), ('Reuter', 'NN')
            ]

        actual = postagger.PosTagger(data).execute()

        self.assertEqual(expected, actual)
