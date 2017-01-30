from unittest import TestCase

from app.lib.nlp import counter


class CounterTestCase(TestCase):
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
        expected = {
                'Gulf': 1, 'Applied': 1, 'Technologies': 1, 'Inc': 1,
                'said': 2, 'it': 2, 'sold': 1, 'its': 1, 'subsidiaries': 1,
                'engaged': 1, 'in': 1, 'pipeline': 1, 'and': 1, 'terminal': 1,
                'operations': 1, 'for': 1, '12.2': 1, 'mln': 1, 'dlrs': 1,
                '.': 2, 'The': 1, 'company': 1, 'the': 1, 'sale': 1, 'is': 1,
                'subject': 1, 'to': 1, 'certain': 1, 'post': 1, 'closing': 1,
                'adjustments': 1, ',': 1, 'which': 1, 'did': 1, 'not': 1,
                'explain': 1, 'Reuter': 1
            }

        actual = counter.Counter(data).execute()

        self.assertEqual(expected, actual)
