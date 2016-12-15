from collections import OrderedDict

from django.test import TestCase

from app.lib import helpers


class HelpersTestCase(TestCase):
    def setUp(self):
        pass

    def test_sort_exceptions(self):
        self.assertRaises(ValueError, helpers.sort, {}, by='foo')
        self.assertRaises(ValueError, helpers.sort, {}, cast='foo')

    def test_sort_defaults(self):
        data = {'one': 1, 'two': 2, 'three': 3}
        expected = OrderedDict([('one', 1), ('two', 2), ('three', 3)])

        actual = helpers.sort(data, by='value', cast=None, desc=False)

        self.assertDictEqual(expected, actual)

    def test_sort_by_value_desc(self):
        data = {'one': 1, 'two': 2, 'three': 3}
        expected = OrderedDict([('three', 3), ('two', 2), ('one', 1)])

        actual = helpers.sort(data, by='value', cast=None, desc=True)

        self.assertDictEqual(expected, actual)

    def test_sort_by_key(self):
        data = {'one': 1, 'two': 2, 'three': 3}
        expected = OrderedDict([('one', 1), ('three', 3), ('two', 2)])

        actual = helpers.sort(data, by='key',  cast=None, desc=False)

        self.assertDictEqual(expected, actual)

    def test_sort_by_key_desc(self):
        data = {'one': 1, 'two': 2, 'three': 3}
        expected = OrderedDict([('two', 2), ('three', 3), ('one', 1)])

        actual = helpers.sort(data, by='key', cast=None, desc=True)

        self.assertDictEqual(expected, actual)

    def test_sort_by_key_cast_int_desc(self):
        data = {'1': '1.4', '2': 5.2, '3': '3.3'}
        expected = OrderedDict([('3', '3.3'), ('2', 5.2), ('1', '1.4')])

        actual = helpers.sort(data, by='key', cast=int, desc=True)

        self.assertDictEqual(expected, actual)

    def test_sort_by_value_cast_float(self):
        data = {'1': '1.4', '2': 5.2, '3': '3.3'}
        expected = OrderedDict([('1', '1.4'), ('3', '3.3'), ('2', 5.2)])

        actual = helpers.sort(data, by='value', cast=float, desc=False)

        self.assertDictEqual(expected, actual)

    def test_truncate_defaults(self):
        data = 'a' * 55
        expected = 'a' * 50 + '...'

        actual = helpers.truncate(data, length=50)

        self.assertEqual(expected, actual)

    def test_truncate_return_unchanged(self):
        data = ['foo', '']
        expected = ['foo', '']

        actual = [helpers.truncate(item, length=3) for item in data]

        self.assertListEqual(expected, actual)
