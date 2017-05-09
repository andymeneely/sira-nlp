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
                (1, 'Gulf', 'Gulf', 'gulf', 'NNP', 'B-NP'),
                (2, 'Applied', 'Appli', 'applied', 'NNP', 'I-NP'),
                (
                    3, 'Technologies', 'Technolog', 'technologies', 'NNPS',
                    'I-NP'
                ),
                (4, 'Inc', 'Inc', 'inc', 'NNP', 'I-NP'),
                (5, 'said', 'said', 'say', 'VBD', 'B-VP'),
                (6, 'it', 'it', 'it', 'PRP', 'B-NP'),
                (7, 'sold', 'sold', 'sell', 'VBD', 'B-VP'),
                (8, 'its', 'it', 'it', 'PRP$', 'B-NP'),
                (9, 'subsidiaries', 'subsidiari', 'subsidiary', 'NNS', 'I-NP'),
                (10, 'engaged', 'engag', 'engage', 'VBN', 'B-VP'),
                (11, 'in', 'in', 'in', 'IN', 'B-PP'),
                (12, 'pipeline', 'pipelin', 'pipeline', 'NN', 'B-NP'),
                (13, 'and', 'and', 'and', 'CC', 'O'),
                (14, 'terminal', 'termin', 'terminal', 'JJ', 'B-NP'),
                (15, 'operations', 'oper', 'operation', 'NNS', 'I-NP'),
                (16, 'for', 'for', 'for', 'IN', 'B-PP'),
                (17, '12.2', '12.2', '12.2', 'CD', 'B-NP'),
                (18, 'mln', 'mln', 'mln', 'NN', 'I-NP'),
                (19, 'dlrs', 'dlr', 'dlrs', 'NN', 'I-NP'),
                (20, '.', '.', '.',  '.', 'O'),
                (21, 'The', 'The', 'the', 'DT', 'B-NP'),
                (22, 'company', 'compani', 'company', 'NN', 'I-NP'),
                (23, 'said', 'said', 'say', 'VBD', 'B-VP'),
                (24, 'the', 'the', 'the', 'DT', 'B-NP'),
                (25, 'sale', 'sale', 'sale', 'NN', 'I-NP'),
                (26, 'is', 'is', 'be', 'VBZ', 'B-VP'),
                (27, 'subject', 'subject', 'subject', 'JJ', 'B-NP'),
                (28, 'to', 'to', 'to', 'TO', 'B-VP'),
                (29, 'certain', 'certain', 'certain', 'JJ', 'B-NP'),
                (30, 'post', 'post', 'post', 'NN', 'I-NP'),
                (31, 'closing', 'close', 'close', 'NN', 'I-NP'),
                (32, 'adjustments', 'adjust', 'adjustment', 'NNS', 'I-NP'),
                (33, ',', ',', ',', ',', 'O'),
                (34, 'which', 'which', 'which', 'WDT', 'B-NP'),
                (35, 'it', 'it', 'it', 'PRP', 'B-NP'),
                (36, 'did', 'did', 'do', 'VBD', 'B-VP'),
                (37, 'not', 'not', 'not', 'RB', 'I-VP'),
                (38, 'explain', 'explain', 'explain', 'VB', 'I-VP'),
                (39, '.', '.', '.',  '.', 'O'),
                (40, 'Reuter', 'Reuter', 'reuter', 'NN', 'B-NP'),
            ]
        actual = summarizer.Summarizer(data).execute()

        self.assertCountEqual(expected, actual)
