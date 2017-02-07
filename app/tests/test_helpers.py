"""
@AUTHOR: nuthanmunaiah
"""
import csv

from unittest import TestCase
from collections import OrderedDict

from app.lib import helpers
from app.lib.nlp import VERBS_PATH


class HelpersTestCase(TestCase):
    def setUp(self):
        pass

    def test_get_verbs(self):
        keys, values = set(), set()
        with open(VERBS_PATH) as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) > 1:
                    for item in row[1:]:
                        keys.add(item)
                    values.add(row[0])
        expected = (keys, values)

        actual = helpers.get_verbs(VERBS_PATH)

        self.assertCountEqual(expected[0], list(actual.keys()))
        self.assertCountEqual(
                expected[1] - set(['shot', 'overshot']),
                list(set(list(actual.values())))
            )
        expected = 'shoot'
        for key in ['shot', 'shoots', 'shooting', 'shot', 'shot']:
            self.assertEqual(expected, actual[key], msg='Key: {}'.format(key))
        expected = 'overshoot'
        for key in ['overshot', 'overshoots', 'overshooting']:
            self.assertEqual(expected, actual[key], msg='Key: {}'.format(key))

    def test_parse_bugids(self):
        data = [
                # Patterns that SHOULD BE recognized
                'BUG=589630\r\n',
                'BUG= 586985, 613948',
                'BUG= 41156',
                'BUG=61406',
                'BUG=612140,581716,602701',
                'BUG=604427, 609013, 612397',
                'BUG=470662, 614968, 614952\r\n',
                (
                    'BUG=364417, 366042, 364391, 403987, 403363, 405125, '
                    '417752, 459576, 482050, 564571, 571534, 588598, 596002'
                ),
                'BUG=chromium:61356',
                'BUG=chromium:639321,459361',
                (
                    'BUG=chromium:648031,chromium:648135,648063,607283,645532,'
                    'chromium:648074'
                ),
                'BUG=chromium:575167, chromium:650655',
                'BUG=chromium:609831,chromium:613947,v8:5049"',
                'BUG=chromium:644033,chromium:637050,648462,chromium:647807',
                (
                    'BUG=chromium:648031,chromium:648135,648063,607283,645532,'
                    'chromium:648074'
                ),
                'BUG=chromium:613321, webrtc:5608',
                'BUG=478714.',
                (
                    'BUG=https://code.google.com/p/chromium/issues/detail?id'
                    '=397177'
                ),
                'BUG= http://crbug.com/14508',
                'BUG=http://crbug.com/18725',
                'BUG=11007\nBUG=16535',
                'BUG=b/27827591, 549781',
                (
                    'BUG=649539,649291,574611,649579,v8:5378,https://github.'
                    'com/dart-lang/sdk/issues/27412,chromium:638366'
                ),
                (
                    'BUG=webrtc:5949,622062,544330,638343,629679,620494,607344'
                    ',637561,https://github.com/dart-lang/sdk/issues/27005,'
                    '637037,611020,604452,chromium:628770,635421,605572,None,'
                    'chromium:448050,626364,598405,none,629863,635877,623207,'
                    '638295'
                ),
            ] + [
                # Patterns that SHOULD NOT BE recognized
                'BUG=',
                'BUG=\r\n',
                'BUG=NONE',
                'BUG=NONE\r\n',
                'BUG=None',
                'BUG=none',
                'BUG=n/a',
                'BUG=none\r\n',
                'BUG=skia:5307',
                'BUG=webrtc:5805',
                'BUG=catapult:#2309',
                'BUG=v8:4907',
                'BUG=internal b/28110563',
                'BUG=flutter/flutter#3804',
                'BUG=b/31767249',
                'BUG=#27238',
                'BUG=b:26700652\r\n',
                'FOO BAR BAZ',
            ]
        expected = [
                # Bug IDs recognized
                [589630],
                [586985, 613948],
                [41156],
                [61406],
                [612140, 581716, 602701],
                [604427, 609013, 612397],
                [470662, 614968, 614952],
                [
                    364417, 366042, 364391, 403987, 403363, 405125, 417752,
                    459576, 482050, 564571, 571534, 588598, 596002
                ],
                [61356],
                [639321, 459361],
                [648031, 648135, 648063, 607283, 645532, 648074],
                [575167, 650655],
                [609831, 613947],
                [644033, 637050, 648462, 647807],
                [648031, 648135, 648063, 607283, 645532, 648074],
                [613321],
                [478714],
                [397177],
                [14508],
                [18725],
                [11007, 16535],
                [549781],
                [649539, 649291, 574611, 649579, 638366],
                [
                    622062, 544330, 638343, 629679, 620494, 607344, 637561,
                    637037, 611020, 604452, 628770, 635421, 605572, 448050,
                    626364, 598405, 629863, 635877, 623207, 638295
                ],
            ] + [
                # Empty lists indicating that no bug IDs were recognized
                list() for i in range(0, 18)
            ]

        actual = [helpers.parse_bugids(item) for item in data]

        self.assertEqual(expected, actual)

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

    def test_to_int(self):
        self.assertEqual(10, helpers.to_int('10'))
        self.assertIsNone(helpers.to_int('chromium:1234'))

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
