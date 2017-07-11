"""
@AUTHOR: nuthanmunaiah
"""
import csv
import datetime
import json
import queue
import tempfile

from unittest import TestCase, skip
from collections import OrderedDict

from app.lib import helpers
from app.lib.nlp import VERBS_PATH

from app.tests.testfiles import *


class HelpersTestCase(TestCase):
    def setUp(self):
        pass

    def test_get_quoted_text(self):
        # Sub-Test 1
        data = (
                "On 2016/05/14 08:43:40, chrishtr wrote:\n> Not unless we \"unr"
                "oll\" them or similar?\n> \n> https://docs.google.com/document"
                "/d/1Tzggk5iFfSIebUxUUWaa3UX_6Uo2yUPVh8AYAWLt05Q/edit\n\nNo, we"
                " can't simply unroll an effect node. As jbroman@ pointed out, "
                "unrolling an effect node changes the rendered result of displa"
                "y list. Because effects apply on an isolated group (i.e. stack"
                "ing context), it is inherently ill-defined to have discontiguo"
                "us effect nodes.\n\nThe only effect that exhibits this \"unrol"
                "ling\" behavior is opacity+transform-style:preserve-3d, which "
                "applies opacity to each planes individually. Debatable, but I "
                "think this behavior is sort of useful and intuitive (and is wh"
                "at vendors implemented). Apply opacity to a teapot, then you g"
                "et a ghostly teapot, instead of a slide of a teapot's picture."
                " This special case is better handled at CSS-to-property-tree l"
                "evel than polluting our well-defined property tree semantics."
            )
        expected = (
                "Not unless we \"unroll\" them or similar?\n\nhttps://docs.goog"
                "le.com/document/d/1Tzggk5iFfSIebUxUUWaa3UX_6Uo2yUPVh8AYAWLt05Q"
                "/edit"
            )
        actual = helpers.get_quoted_text(data)
        self.assertEqual(expected, actual)

        # Sub-Test 2
        # Comment 4 quotes Comment 3 on Line 30 of: https://codereview.chromium.org/1971023005/diff/20001/third_party/WebKit/Source/platform/graphics/paint/EffectPaintPropertyNode.h
        data = (
                "On 2016/05/18 at 16:42:19, chrishtr wrote:\n> On 2016/05/16 at"
                " 22:07:43, trchen wrote:\n> > On 2016/05/14 08:43:39, chrishtr"
                " wrote:\n> > > How about:\n> > > \n> > > enum Type {\n> > >   "
                "Flatten,\n> > >   FlattenAndOpacity\n> > > }\n> > \n> > I feel"
                " that's sort of redundant because it makes no sense to perform"
                " an effect without flattening. So is making an isolated group."
                " I don't think prefixing every effect type with FlattenAndIsol"
                "ateThen provides any useful information...\n> \n> I think it's"
                " useful, because Noop sounds to a person reading this code as "
                "if it does nothing, when in fact it flattens. It's better to b"
                "e explicit about what code does, even if it sounds redundant t"
                "o an expert.\n\nI wouldn't prefix everything, but \"OnlyFlatte"
                "ning\" or similar would be clearer than no-op, since, as chris"
                "htr points out, it doesn't do nothing."
            )
        expected = (
                "\nI think it's useful, because Noop sounds to a person reading t"
                "his code as if it does nothing, when in fact it flattens. It's"
                " better to be explicit about what code does, even if it sounds"
                " redundant to an expert."
            )
        actual = helpers.get_quoted_text(data)
        self.assertEqual(expected, actual)

        # Sub-Test 3
        # Comment 2 quotes Comment 1 on Line 24 of: https://codereview.chromium.org/2000083002/diff/1/net/disk_cache/simple/simple_synchronous_entry.cc
        data = (
                "On 2016/05/23 11:32:52, gavinp wrote:\n> This can be removed n"
                "ow.\nDone."
            )
        expected = (
                "This can be removed now."
            )
        actual = helpers.get_quoted_text(data)
        self.assertEqual(expected, actual)

        # Sub-Test 4
        # Comment 1 does not quote anything on Line 151 of: https://codereview.chromium.org/1071273002/diff/1/ui/ozone/platform/drm/gpu/gbm_map_pixmap_intel.cc
        data = (
                "As comment said, this CL has glitch and crash bugs. I'm debugg"
                "ing how can I workaround. This is why I submit few CL about ze"
                "ro-copy recently.\n\n@kalyank_ ,dose drm_intel_bo_gem_export_t"
                "o_prime() unref drm_intel_bo instance internally? after drm_in"
                "tel_bo_gem_export_to_prime(), if I call  drm_intel_bo_unrefere"
                "nce() , gpu process sometimes die with error log \"intel_do_fl"
                "ush_locked failed: Invalid argument\"\n"
            )
        expected = (
                ""
            )
        actual = helpers.get_quoted_text(data)
        self.assertEqual(expected, actual)

        # Sub-Test 5
        # Comment 5 quotes Comment 3 on Line 78 of: https://codereview.chromium.org/1996173002/diff/20001/mojo/common/value_type_converters.h
        data = (
                "On 2016/05/23 17:07:05, Devlin wrote:\n> On 2016/05/20 22:46:4"
                "3, Ken Rockot wrote:\n> > On 2016/05/20 at 17:29:25, Devlin wr"
                "ote:\n> > > Sad copy :(\n> > \n> > I think we can avoid this c"
                "opy by defining a new\n> > mojo::ArrayTraits<base::BinaryValue"
                "> specialization, and then this can actually\n> > just retu"
                "rn a ref to the BinaryValue and the bindings will know how to "
                "treat it\n> > like a uint8 array. +yzshen@ to confirm this."
                "\n> \n> base::BinaryValue doesn't have any kind of Resize() fu"
                "nctionality (and given\n> it's backed by a POD array, there's "
                "no guaranteed efficient way to expose one).\n\nOne possible so"
                "lution is to use a struct for BinaryValue, instead of an array"
                ". Then you can write a StructTraits instead of an ArrayTraits."
                "\n\nstruct BinaryValue {\n  array<uint8> value;\n};\n\nStructT"
                "raits<mojom::BinaryValue, base::BinaryValue*> {\n};\n\nSomethi"
                "ng like that."
            )
        expected = (
                "\nbase::BinaryValue doesn't have any kind of Resize() function"
                "ality (and given\nit's backed by a POD array, there's no guara"
                "nteed efficient way to expose one)."
            )
        actual = helpers.get_quoted_text(data)
        self.assertEqual(expected, actual)

        # Sub-Test 6
        # Comment 2 quotes Comment 1 on Line 209 of: https://codereview.chromium.org/1318783003/diff/100001/src/shared/natives.h
        data = (
                "On 2015/08/28 07:16:49, Mads Ager (google) wrote:\n> I think w"
                "e can share the implementation of length and just have a Strin"
                "gLength\n> native? Lenght is from BaseArray I think, so it sho"
                "uld be fine to just assert\n> that the argument is a OneByteSt"
                "ring or a TwoByteString and then return\n> BaseArray::cast(obj"
                "ect)->length()?\n\nDone."
            )
        expected = (
                "I think we can share the implementation of length and just hav"
                "e a StringLength\nnative? Lenght is from BaseArray I think, so"
                " it should be fine to just assert\nthat the argument is a OneB"
                "yteString or a TwoByteString and then return\nBaseArray::cast("
                "object)->length()?"
            )
        actual = helpers.get_quoted_text(data)
        self.assertEqual(expected, actual)

    def test_chunk(self):
        data = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k']
        expected = [
                ['a', 'b'], ['c', 'd'], ['e', 'f'], ['g', 'h'], ['i', 'j'],
                ['k']
            ]
        actual = list(helpers.chunk(data, 2))
        self.assertListEqual(expected, actual)

    def test_clean(self):
        data = 'It would be great if we could land this if things look ok. I' \
               ' will address michael\'s comments in a followup when he gets' \
               ' back on the 5th.\n\nhttps://codereview.chromium.org/2956373' \
               '002/diff/100001/content/browser/appcache/appcache_subresourc' \
               'e_url_factory.h\nFile content/browser/appcache/appcache_subr' \
               'esource_url_factory.h (right):\n\nhttps://codereview.chromiu' \
               'm.org/2956373002/diff/100001/content/browser/appcache/appcac' \
               'he_subresource_url_factory.h#newcode24\ncontent/browser/appc' \
               'ache/appcache_subresource_url_factory.h:24: struct Subresour' \
               'ceLoadInfo {\nOn 2017/06/30 01:31:15, jam wrote:\n> nit: why' \
               ' is this in this header if it\'s not referenced in this file' \
               '? seems like\n> it should be in appcache_request_handler.h?' \
               '\n\nIt is populated in the factory cc file. I thought it is ' \
               'better to have it there.'
        expected = 'It would be great if we could land this if things look o' \
                   'k. I will address michael\'s comments in a followup when' \
                   ' he gets back on the 5th.\n\nIt is populated in the fact' \
                   'ory cc file. I thought it is better to have it there.'
        actual = helpers.clean(data)
        self.assertEqual(expected, actual)

    def test_get_elapsed(self):
        data = (
                datetime.datetime(2017, 1, 1, 0, 0, 0, 0),
                datetime.datetime(2017, 1, 1, 0, 1, 0, 0)
            )
        expected = 1
        actual = helpers.get_elapsed(*data)
        self.assertEqual(expected, actual)

    def test_get_json(self):
        actual = helpers.get_json(
                'https://codereview.chromium.org/api/201', None
            )
        self.assertTrue(type(actual) is tuple)
        self.assertEqual(200, actual[0])
        self.assertTrue(type(actual[1]) is dict)

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

    @skip('Skipping test as the functionality being tested is not complete.')
    def test_line_changed(self):
        # Sub-Test 1
        line_number = 113
        with open(DIFF_4001_5001_PATH, 'r') as f:
            patch_a = f.read()
        with open(DIFF_10001_11001_PATH, 'r') as f:
            patch_b = f.read()

        expected = True
        actual = helpers.line_changed(line_number, patch_a, patch_b)
        self.assertEqual(expected, actual)

    def test_load_json_w_sanitization(self):
        data = expected = {'message': 'hello world!!!'}
        with tempfile.TemporaryDirectory() as tempdir:
            filepath = os.path.join(tempdir, 'foo.json')
            with open(filepath, 'w') as file:
                json.dump(data, file)
            actual = helpers.load_json(filepath, sanitize=True)
            self.assertEqual(expected, actual)

    def test_load_json_wo_sanitization(self):
        data = expected = {'message': 'hello world!!!'}
        with tempfile.TemporaryDirectory() as tempdir:
            filepath = os.path.join(tempdir, 'foo.json')
            with open(filepath, 'w') as file:
                json.dump(data, file)
            actual = helpers.load_json(filepath, sanitize=False)
            self.assertEqual(expected, actual)

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

    def test_sleep(self):
        helpers.sleep(1)

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

    def test_to_list(self):
        data = queue.Queue()
        for i in range(0, 10):
            data.put(i)
        expected = list(range(0, 10))
        actual = helpers.to_list(data)
        self.assertListEqual(expected, actual)

    def test_to_querystring(self):
        data = {'messages': True}
        expected = 'messages=True'
        actual = helpers.to_querystring(data)
        self.assertEqual(expected, actual)
