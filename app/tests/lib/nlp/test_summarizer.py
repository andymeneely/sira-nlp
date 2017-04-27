from unittest import TestCase

from app.lib.nlp import summarizer


class SummarizerTestCase(TestCase):
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
                (1, 'Gulf', 'gulf', 'NNP'),
                (2, 'Applied', 'applied', 'NNP'),
                (3, 'Technologies', 'technologies', 'NNPS'),
                (4, 'Inc', 'inc', 'NNP'),
                (5, 'said', 'say', 'VBD'),
                (6, 'it', 'it', 'PRP'),
                (7, 'sold', 'sell', 'VBD'),
                (8, 'its', 'it', 'PRP$'),
                (9, 'subsidiaries', 'subsidiary', 'NNS'),
                (10, 'engaged', 'engage', 'VBN'),
                (11, 'in', 'in', 'IN'),
                (12, 'pipeline', 'pipeline', 'NN'),
                (13, 'and', 'and', 'CC'),
                (14, 'terminal', 'terminal', 'JJ'),
                (15, 'operations', 'operation', 'NNS'),
                (16, 'for', 'for', 'IN'),
                (17, '12.2', '12.2', 'CD'),
                (18, 'mln', 'mln', 'NN'),
                (19, 'dlrs', 'dlrs', 'NN'),
                (20, '.', '.', '.'),
                (21, 'The', 'the', 'DT'),
                (22, 'company', 'company', 'NN'),
                (23, 'said', 'say', 'VBD'),
                (24, 'the', 'the', 'DT'),
                (25, 'sale', 'sale', 'NN'),
                (26, 'is', 'be', 'VBZ'),
                (27, 'subject', 'subject', 'JJ'),
                (28, 'to', 'to', 'TO'),
                (29, 'certain', 'certain', 'JJ'),
                (30, 'post', 'post', 'NN'),
                (31, 'closing', 'close', 'NN'),
                (32, 'adjustments', 'adjustment', 'NNS'),
                (33, ',', ',', ','),
                (34, 'which', 'which', 'WDT'),
                (35, 'it', 'it', 'PRP'),
                (36, 'did', 'do', 'VBD'),
                (37, 'not', 'not', 'RB'),
                (38, 'explain', 'explain', 'VB'),
                (39, '.', '.', '.'),
                (40, 'Reuter', 'reuter', 'NN'),
            ]
        actual = summarizer.Summarizer(data).execute()

        self.assertCountEqual(expected, actual)
