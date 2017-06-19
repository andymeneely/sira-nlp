from unittest import TestCase

from app.lib.nlp import chunktagger


class ChunkTaggerTestCase(TestCase):
    def setUp(self):
        pass

    def test_execute(self):
        data = [
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
        expected = [
                ('Gulf', 'B-NP'), ('Applied', 'I-NP'),
                ('Technologies', 'I-NP'), ('Inc', 'I-NP'), ('said', 'B-VP'),
                ('it', 'B-NP'), ('sold', 'B-VP'), ('its', 'B-NP'),
                ('subsidiaries', 'I-NP'), ('engaged', 'B-VP'), ('in', 'B-PP'),
                ('pipeline', 'B-NP'), ('and', 'O'), ('terminal', 'B-NP'),
                ('operations', 'I-NP'), ('for', 'B-PP'), ('12.2', 'B-NP'),
                ('mln', 'I-NP'), ('dlrs', 'I-NP'), ('.', 'O'), ('The', 'B-NP'),
                ('company', 'I-NP'), ('said', 'B-VP'), ('the', 'B-NP'),
                ('sale', 'I-NP'), ('is', 'B-VP'), ('subject', 'B-NP'),
                ('to', 'B-VP'), ('certain', 'B-NP'), ('post', 'I-NP'),
                ('closing', 'I-NP'), ('adjustments', 'I-NP'), (',', 'O'),
                ('which', 'B-NP'), ('it', 'B-NP'), ('did', 'B-VP'),
                ('not', 'I-VP'), ('explain', 'I-VP'), ('.', 'O'),
                ('Reuter', 'B-NP')
            ]

        actual = chunktagger.ChunkTagger().parse(data)

        self.assertEqual(expected, actual)
