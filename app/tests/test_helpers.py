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

from app.tests import mocks
from app.tests.testfiles import *


class HelpersTestCase(TestCase):
    def setUp(self):
        pass

    def test_to_json(self):
        data = (
                '{"sentences":[{"index":0,"parse":"(ROOT\\n  (S\\n    (NP (PRP '
                'I))\\n    (VP (VBP am)\\n      (NP (DT the) (NN walrus)))\\n  '
                '  (. .)))","basicDependencies":[{"dep":"ROOT","governor":0,"go'
                'vernorGloss":"ROOT","dependent":4,"dependentGloss":"walrus"},{'
                '"dep":"nsubj","governor":4,"governorGloss":"walrus","dependent'
                '":1,"dependentGloss":"I"},{"dep":"cop","governor":4,"governorG'
                'loss":"walrus","dependent":2,"dependentGloss":"am"},{"dep":"de'
                't","governor":4,"governorGloss":"walrus","dependent":3,"depend'
                'entGloss":"the"},{"dep":"punct","governor":4,"governorGloss":"'
                'walrus","dependent":5,"dependentGloss":"."}],"enhancedDependen'
                'cies":[{"dep":"ROOT","governor":0,"governorGloss":"ROOT","depe'
                'ndent":4,"dependentGloss":"walrus"},{"dep":"nsubj","governor":'
                '4,"governorGloss":"walrus","dependent":1,"dependentGloss":"I"}'
                ',{"dep":"cop","governor":4,"governorGloss":"walrus","dependent'
                '":2,"dependentGloss":"am"},{"dep":"det","governor":4,"governor'
                'Gloss":"walrus","dependent":3,"dependentGloss":"the"},{"dep":"'
                'punct","governor":4,"governorGloss":"walrus","dependent":5,"de'
                'pendentGloss":"."}],"enhancedPlusPlusDependencies":[{"dep":"RO'
                'OT","governor":0,"governorGloss":"ROOT","dependent":4,"depende'
                'ntGloss":"walrus"},{"dep":"nsubj","governor":4,"governorGloss"'
                ':"walrus","dependent":1,"dependentGloss":"I"},{"dep":"cop","go'
                'vernor":4,"governorGloss":"walrus","dependent":2,"dependentGlo'
                'ss":"am"},{"dep":"det","governor":4,"governorGloss":"walrus","'
                'dependent":3,"dependentGloss":"the"},{"dep":"punct","governor"'
                ':4,"governorGloss":"walrus","dependent":5,"dependentGloss":"."'
                '}],"sentimentValue":"2","sentiment":"Neutral","tokens":[{"inde'
                'x":1,"word":"I","originalText":"I","characterOffsetBegin":0,"c'
                'haracterOffsetEnd":1,"pos":"PRP","before":"","after":" "},{"in'
                'dex":2,"word":"am","originalText":"am","characterOffsetBegin":'
                '2,"characterOffsetEnd":4,"pos":"VBP","before":" ","after":" "}'
                ',{"index":3,"word":"the","originalText":"the","characterOffset'
                'Begin":5,"characterOffsetEnd":8,"pos":"DT","before":" ","after'
                '":" \x1a "},{"index":4,"word":"walrus","originalText":"walrus"'
                ',"characterOffsetBegin":11,"characterOffsetEnd":17,"pos":"NN",'
                '"before":" \x1a ","after":""},{"index":5,"word":".","originalT'
                'ext":".","characterOffsetBegin":17,"characterOffsetEnd":18,"po'
                's":".","before":"","after":""}]}]}'
            )

        expected = {'sentences': [{'sentimentValue': '2', 'tokens': [{'after': ' ', 'originalText': 'I', 'pos': 'PRP', 'characterOffsetEnd': 1, 'characterOffsetBegin': 0, 'word': 'I', 'index': 1, 'before': ''}, {'after': ' ', 'originalText': 'am', 'pos': 'VBP', 'characterOffsetEnd': 4, 'characterOffsetBegin': 2, 'word': 'am', 'index': 2, 'before': ' '}, {'after': '  ', 'originalText': 'the', 'pos': 'DT', 'characterOffsetEnd': 8, 'characterOffsetBegin': 5, 'word': 'the', 'index': 3, 'before': ' '}, {'after': '', 'originalText': 'walrus', 'pos': 'NN', 'characterOffsetEnd': 17, 'characterOffsetBegin': 11, 'word': 'walrus', 'index': 4, 'before': '  '}, {'after': '', 'originalText': '.', 'pos': '.', 'characterOffsetEnd': 18, 'characterOffsetBegin': 17, 'word': '.', 'index': 5, 'before': ''}], 'parse': '(ROOT\n  (S\n    (NP (PRP I))\n    (VP (VBP am)\n      (NP (DT the) (NN walrus)))\n    (. .)))', 'sentiment': 'Neutral', 'basicDependencies': [{'governor': 0, 'governorGloss': 'ROOT', 'dependent': 4, 'dep': 'ROOT', 'dependentGloss': 'walrus'}, {'governor': 4, 'governorGloss': 'walrus', 'dependent': 1, 'dep': 'nsubj', 'dependentGloss': 'I'}, {'governor': 4, 'governorGloss': 'walrus', 'dependent': 2, 'dep': 'cop', 'dependentGloss': 'am'}, {'governor': 4, 'governorGloss': 'walrus', 'dependent': 3, 'dep': 'det', 'dependentGloss': 'the'}, {'governor': 4, 'governorGloss': 'walrus', 'dependent': 5, 'dep': 'punct', 'dependentGloss': '.'}], 'index': 0, 'enhancedDependencies': [{'governor': 0, 'governorGloss': 'ROOT', 'dependent': 4, 'dep': 'ROOT', 'dependentGloss': 'walrus'}, {'governor': 4, 'governorGloss': 'walrus', 'dependent': 1, 'dep': 'nsubj', 'dependentGloss': 'I'}, {'governor': 4, 'governorGloss': 'walrus', 'dependent': 2, 'dep': 'cop', 'dependentGloss': 'am'}, {'governor': 4, 'governorGloss': 'walrus', 'dependent': 3, 'dep': 'det', 'dependentGloss': 'the'}, {'governor': 4, 'governorGloss': 'walrus', 'dependent': 5, 'dep': 'punct', 'dependentGloss': '.'}], 'enhancedPlusPlusDependencies': [{'governor': 0, 'governorGloss': 'ROOT', 'dependent': 4, 'dep': 'ROOT', 'dependentGloss': 'walrus'}, {'governor': 4, 'governorGloss': 'walrus', 'dependent': 1, 'dep': 'nsubj', 'dependentGloss': 'I'}, {'governor': 4, 'governorGloss': 'walrus', 'dependent': 2, 'dep': 'cop', 'dependentGloss': 'am'}, {'governor': 4, 'governorGloss': 'walrus', 'dependent': 3, 'dep': 'det', 'dependentGloss': 'the'}, {'governor': 4, 'governorGloss': 'walrus', 'dependent': 5, 'dep': 'punct', 'dependentGloss': '.'}]}]}

        actual = helpers.to_json(data)
        self.assertDictEqual(expected, actual)

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

    def test_get_module_path(self):
        data = [
          'gpu/gpu.gyp',
          'tests/MatrixTest.cpp',
          'chrome/renderer/content_settings_observer.cc',
          'chrome/browser/devtools/devtools_window.cc',
          'gm/cubicpaths.cpp',
          'AUTHORS',
          'src/vm/service_api_impl.cc',
          'chrome/browser/devtools/devtools_window.h',
          'chrome/browser/guest_view/chrome_guest_view_manager_delegate.cc',
          'chrome/browser/task_management/sampling/shared_sampler.h',
          'chrome/browser/task_manager/providers/web_contents/panel_task.cc',
          'components/memory_coordinator/public/interfaces/child_memory_coordi'
          'nator.mojom',
          'content/browser/accessibility/browser_accessibility_auralinux.cc',
          'content/ppapi_plugin/ppapi_thread.h',
          'content/renderer/device_sensors/device_orientation_event_pump_unitt'
          'est.cc',
          'content/shell/browser/shell_content_browser_client.cc',
          'content/shell/browser/shell_devtools_manager_delegate.h'
        ]
        expected = [
          'gpu',
          'tests',
          'chrome/renderer',
          'chrome/browser/devtools',
          'gm',
          '',
          'src/vm',
          'chrome/browser/devtools',
          'chrome/browser/guest_view',
          'chrome/browser/task_management/sampling',
          'chrome/browser/task_manager/providers/web_contents',
          'components/memory_coordinator/public/interfaces',
          'content/browser/accessibility',
          'content/ppapi_plugin',
          'content/renderer/device_sensors',
          'content/shell/browser',
          'content/shell/browser'
        ]
        actual = [helpers.get_module_path(item) for item in data]
        self.assertEqual(expected, actual)

    def test_get_parent(self):
        # Mocking Data
        # Reference URI: /2886483002/diff/160001/net/http/http_cache_writers.cc
        comments = list()

        # Case: No parent
        data = 'What drove adding the network transaction here rather than o' \
               'n construction?  It\'s only the first HC::T that\'ll add a n' \
               'etwork transaction, so having it as part of the AddTransacti' \
               'on method feels a bit funny.  '
        actual = helpers.get_parent(data, comments)
        self.assertIsNone(actual, msg='None')

        comment = mocks.Comment()
        comment.id = 1
        comment.posted = '2017-05-18 01:02:54.688440'
        comment.line = 28
        comment.author = 'rdsmith@chromium.org'
        text = 'What drove adding the network transaction here rather than o' \
               'n construction?  It\'s only the first HC::T that\'ll add a n' \
               'etwork transaction, so having it as part of the AddTransacti' \
               'on method feels a bit funny.  '
        comment.text = text
        comments.append(comment)

        # Case: Single
        data = 'On 2017/05/18 at 01:02:54, Randy Smith (Not in Mondays) wrot' \
               'e:\n> What drove adding the network transaction here rather ' \
               'than on construction?  It\'s only the first HC::T that\'ll a' \
               'dd a network transaction, so having it as part of the AddTra' \
               'nsaction method feels a bit funny.\n\nI am hoping writers ca' \
               'n be a member variable of ActiveEntry instead of a unique_pt' \
               'r and in that case writers will be created even before a tra' \
               'nsaction is added to it.'
        expected = None
        for comment in comments:  # pragma: no cover
            if comment.id == 1:
                expected = comment
                break
        actual = helpers.get_parent(data, comments)

        self.assertEqual(expected.id, actual.id, msg='ID: Single')
        self.assertEqual(expected.text, actual.text, msg='Text: Single')

        comment = mocks.Comment()
        comment.id = 2
        comment.posted = '2017-05-18 20:59:44.694320'
        comment.line = 28
        comment.author = 'shivanisha@chromium.org'
        text = 'I am hoping writers can be a member variable of ActiveEntry ' \
               'instead of a unique_ptr and in that case writers will be cre' \
               'ated even before a transaction is added to it.'
        comment.text = text
        comments.append(comment)

        comment = mocks.Comment()
        comment.id = 3
        comment.posted = '2017-05-24 23:09:18.829590'
        comment.line = 28
        comment.author = 'rdsmith@chromium.org'
        text = 'Hmmm.  Ok.  There\'s a range of design choices here, and I d' \
               'on\'t have a strong feeling that one is better than the othe' \
               'r, but keep the other ones (unique_ptr, separate methods for' \
               ' adding network transaction & HC::Ts, separate methods for a' \
               'dding the first transaction and adding subsequent ones, this' \
               ' method but destroying other network transactions when they ' \
               'come in) in mind as possibilities and make a conscious decis' \
               'ion among them.  '
        comment.text = text
        comments.append(comment)

        comment = mocks.Comment()
        comment.id = 4
        comment.posted = '2017-05-24 23:09:18.990390'
        comment.line = 28
        comment.author = 'rdsmith@chromium.org'
        text = 'Worthwhile adding a DCHECK that network_transaction_ wasn\'t' \
               ' already set?'
        comment.text = text
        comments.append(comment)

        # Case: Multiple
        data = 'On 2017/05/24 at 23:09:18, Randy Smith (Not in Mondays) wrot' \
               'e:\n> Worthwhile adding a DCHECK that network_transaction_ w' \
               'asn\'t already set?\n\nDone'
        expected = None
        for comment in comments:  # pragma: no cover
            if comment.id == 4:
                expected = comment
                break
        actual = helpers.get_parent(data, comments)

        self.assertEqual(expected.id, actual.id, msg='ID: Multiple')
        self.assertEqual(expected.text, actual.text, msg='Text: Multiple')

        comment = mocks.Comment()
        comment.id = 5
        comment.posted = '2017-05-31 19:21:26.490670'
        comment.line = 28
        comment.author = 'shivanisha@chromium.org'
        text = 'Done'
        comment.text = text
        comments.append(comment)

        # Case: Multiple
        data = 'On 2017/05/24 at 23:09:18, Randy Smith (Not in Mondays) wrot' \
               'e:\n> Worthwhile adding a DCHECK that network_transaction_ w' \
               'asn\'t already set?\n\nAdded the dcheck'
        expected = None
        for comment in comments:  # pragma: no cover
            if comment.id == 4:
                expected = comment
                break
        actual = helpers.get_parent(data, comments)

        self.assertEqual(expected.id, actual.id, msg='ID: Multiple')
        self.assertEqual(expected.text, actual.text, msg='Text: Multiple')

    def test_get_parent_no_quote(self):
        # Mocking Data
        # Reference URI: /1282313002/diff/180001/content/common/gpu/
        #                gpu_memory_buffer_factory_io_surface.cc
        comments = list()

        comment = expected = mocks.Comment()
        comment.id = 1
        comment.posted = '2015-08-11 08:20:08.288830'
        comment.line = 132
        comment.author = 'reveman@chromium.org'
        text = 'This is unfortunate. What happens if we remove this if state' \
               'ment? Single plane formats don\'t work unless kIOSurfaceByte' \
               'sPerElement is set?\n\nIn that case, I\'d prefer if we handl' \
               'ed this explicitly using a large \"switch (format)\" stateme' \
               'nt to make it very clear what formats need the plane info an' \
               'd what formats don\'t.'
        comment.text = text
        comments.append(comment)

        data = 'Done.\nI removed the if statement, and it seems to work just' \
               ' fine.\n'

        actual = helpers.get_parent(data, comments)

        self.assertEqual(expected.id, actual.id, msg='ID: No quote')
        self.assertEqual(expected.text, actual.text, msg='Text: No quote')

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
