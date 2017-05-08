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
                (1, 'Gulf', 'Gulf', 'gulf', 'NNP'),
                (2, 'Applied', 'Appli', 'applied', 'NNP'),
                (3, 'Technologies', 'Technolog', 'technologies', 'NNPS'),
                (4, 'Inc', 'Inc', 'inc', 'NNP'),
                (5, 'said', 'said', 'say', 'VBD'),
                (6, 'it', 'it', 'it', 'PRP'),
                (7, 'sold', 'sold', 'sell', 'VBD'),
                (8, 'its', 'it', 'it', 'PRP$'),
                (9, 'subsidiaries', 'subsidiari', 'subsidiary', 'NNS'),
                (10, 'engaged', 'engag', 'engage', 'VBN'),
                (11, 'in', 'in', 'in', 'IN'),
                (12, 'pipeline', 'pipelin', 'pipeline', 'NN'),
                (13, 'and', 'and', 'and', 'CC'),
                (14, 'terminal', 'termin', 'terminal', 'JJ'),
                (15, 'operations', 'oper', 'operation', 'NNS'),
                (16, 'for', 'for', 'for', 'IN'),
                (17, '12.2', '12.2', '12.2', 'CD'),
                (18, 'mln', 'mln', 'mln', 'NN'),
                (19, 'dlrs', 'dlr', 'dlrs', 'NN'),
                (20, '.', '.', '.',  '.'),
                (21, 'The', 'The', 'the', 'DT'),
                (22, 'company', 'compani', 'company', 'NN'),
                (23, 'said', 'said', 'say', 'VBD'),
                (24, 'the', 'the', 'the', 'DT'),
                (25, 'sale', 'sale', 'sale', 'NN'),
                (26, 'is', 'is', 'be', 'VBZ'),
                (27, 'subject', 'subject', 'subject', 'JJ'),
                (28, 'to', 'to', 'to', 'TO'),
                (29, 'certain', 'certain', 'certain', 'JJ'),
                (30, 'post', 'post', 'post', 'NN'),
                (31, 'closing', 'close', 'close', 'NN'),
                (32, 'adjustments', 'adjust', 'adjustment', 'NNS'),
                (33, ',', ',', ',', ','),
                (34, 'which', 'which', 'which', 'WDT'),
                (35, 'it', 'it', 'it', 'PRP'),
                (36, 'did', 'did', 'do', 'VBD'),
                (37, 'not', 'not', 'not', 'RB'),
                (38, 'explain', 'explain', 'explain', 'VB'),
                (39, '.', '.', '.',  '.'),
                (40, 'Reuter', 'Reuter', 'reuter', 'NN'),
            ]
        actual = summarizer.Summarizer(data).execute()

        self.assertCountEqual(expected, actual)
