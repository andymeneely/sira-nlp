import os
import signal
import subprocess

from datetime import datetime

from django.conf import settings
from django.core.management import call_command
from django.db import transaction
from django.test import TransactionTestCase, override_settings
from django.utils.six import StringIO

from app.models import *
from app.lib import helpers
from app.queryStrings import *


def to_datetime(text):
    return datetime.strptime(text, '%Y-%m-%d %H:%M:%S.%f')


class LoaddbTestCase(TransactionTestCase):
    def setUp(self):
        pass

    def test_handle(self):
        call_command('loaddb')

        # Reviews
        expected = (
                [   # 2013
                    12314009
                ] +
                [   # 2015
                    1128633002, 1144393004, 1188433011, 1247623005, 1259853004,
                    1286193008, 1292403004, 1293023003, 1295003003, 1295403003,
                    1299243002, 1304613003, 1308723003, 1318783003, 1321103002,
                    1444413002, 1454003003, 1457243002, 1544273002
                ] +
                [   # 2016
                    1999153002, 2027643002, 2140383005, 2148643002, 2148653002,
                    2148793002, 2149523002, 2150783003, 2151613002, 2151763003,
                    2050053002, 2048483002, 2177983004, 2134723002, 2085023003,
                    2256073002, 2230993004, 2211423003, 2223093002, 2210603002,
                    2189523002, 2168223002
                ]
            )
        actual = list(Review.objects.values_list('id', flat=True))
        self.assertCountEqual(expected, actual, msg='Reviews mismatch.')

        # Bugs
        expected = (
                [   # 2012
                    138542
                ] +
                [   # 2015
                    460986, 492263, 514246, 514551, 517548, 521057, 521826,
                    522049, 522587, 522791, 528486, 534718, 542060, 545318
                ] +
                [   # 2016
                    576270, 583485, 584783, 602509, 606056, 607690, 609260,
                    610176, 613160, 617492, 620126, 624894, 625357, 627655,
                    628110, 628496, 636539, 613918, 619379, 626102, 642598
                ] +
                [   # Manually Added (aka Redacted)
                    618037, 174059
                ]
            )
        actual = list(Bug.objects.values_list('id', flat=True))
        self.assertCountEqual(expected, actual, msg='Bugs mismatch.')

        expected = [
                (618037, 'Bug-Security', 'Redacted'),
                (174059, 'Bug-Security', 'Redacted')
            ]
        actual = list(
                Bug.objects
                .filter(id__in=[618037, 174059])
                .values_list('id', 'type', 'status')
            )
        self.assertCountEqual(expected, actual, msg='Redacted bugs mismatch.')

        # Review to Bug Mappings
        expected = (
                [   # 2013
                    (12314009, 174059)
                ] +
                [   # 2015
                    (1188433011, 492263), (1259853004, 514551),
                    (1286193008, 517548), (1292403004, 521057),
                    (1293023003, 522587), (1295003003, 522049),
                    (1295403003, 460986), (1299243002, 514246),
                    (1304613003, 521826), (1308723003, 522791),
                    (1454003003, 542060)
                ] +
                [   # Review from 2015 and Bug from 2012
                    (1544273002, 138542)
                ] +
                [   # 2016
                    (1999153002, 613160), (2027643002, 609260),
                    (2085023003, 583485), (2134723002, 576270),
                    (2134723002, 620126), (2140383005, 606056),
                    (2148643002, 627655), (2148653002, 602509),
                    (2148793002, 584783), (2149523002, 628496),
                    (2150783003, 617492), (2151613002, 625357),
                    (2151763003, 628110), (2177983004, 618037),
                    (2210603002, 607690), (2223093002, 618037),
                    (2230993004, 636539)
                ] +
                [   # Review from 2016 and Bug from 2015
                    (2050053002, 534718), (2048483002, 545318),
                    (2211423003, 528486)
                ]
            )
        actual = list(ReviewBug.objects.values_list('review_id', 'bug_id'))
        self.assertCountEqual(expected, actual)

        # Vulnerabilities
        expected = (
                [   # 2015
                    ('CVE-2015-1294', 'monorail'),
                    ('CVE-2015-1292', 'monorail'),
                ] +
                [   # 2016
                    ('CVE-2016-1681', 'monorail'),
                    ('CVE-2016-1702', 'monorail'),
                    ('CVE-2016-5167', 'monorail')
                ] +
                [   # Manually Added
                    ('CVE-2016-5165', 'blog'),
                    ('CVE-2016-2845', 'manual'),
                    ('CVE-2013-0908', 'manual')
                ]
            )
        actual = list(Vulnerability.objects.values_list('id', 'source'))
        self.assertCountEqual(expected, actual)

        # Vulnerability to Bug Mappings
        expected = (
                [   # 2015
                    ('CVE-2015-1294', 492263),
                    ('CVE-2015-1292', 522791),
                ] +
                [   # 2016
                    ('CVE-2016-1681', 613160),
                    ('CVE-2016-1702', 609260),
                    ('CVE-2016-5167', 613918),
                    ('CVE-2016-5167', 619379),
                    ('CVE-2016-5167', 626102),
                    ('CVE-2016-5167', 642598)
                ] +
                [   # Manually Added
                    ('CVE-2016-5165', 618037),
                    ('CVE-2016-2845', 542060),
                    ('CVE-2013-0908', 174059)
                ]
            )
        actual = list(VulnerabilityBug.objects.values_list(
                'vulnerability_id', 'bug_id'
            ))
        self.assertCountEqual(expected, actual, msg='Data: VulnerabilityBug')

        # Missed Vulnerability Reviews
        expected = [
                1128633002, 1144393004, 1247623005, 1259853004, 1292403004,
                1444413002, 1544273002, 2085023003, 2134723002, 2168223002,
                2177983004, 2189523002, 2210603002, 2211423003
            ]
        actual = list(
                Review.objects.filter(missed_vulnerability=True)
                .values_list('id', flat=True)
            )
        self.assertCountEqual(expected, actual)

        # Comments
        expected = {
                to_datetime('2015-08-31 07:07:02.637270'): [
                    to_datetime('2015-08-28 07:16:49.330570'),
                    'Same comments about length computations.'
                ],
                to_datetime('2016-08-08 23:53:31.600620'): [
                    to_datetime('2016-08-08 19:01:37.630140'),
                    'Is it actually a cancelAutocomplete?'
                ],
                to_datetime('2016-08-10 23:31:08.030380'): [
                    to_datetime('2016-08-10 23:13:43.524610'),
                    'Please change these to is_worker and is_v8_only.'
                ],
                to_datetime('2016-07-19 17:38:47.630800'): [
                    to_datetime('2016-07-19 12:45:03.109650'),
                    "style: we don't use { } when not needed usually."
                ],
                to_datetime('2016-07-27 22:06:30.261480'): [
                    to_datetime('2016-07-27 20:44:06.925810'),
                    'This was used for autostart modules.'
                ],
                to_datetime('2016-08-08 23:53:32.936720'): [
                    to_datetime('2016-08-08 19:01:37.778730'),
                    'Can we get rid of these?'
                ],
                to_datetime('2015-08-27 06:09:53.292350'): [
                    to_datetime('2015-08-21 19:30:30.486850'),
                    "Can't GetLevelSize() return true even though width and "
                    "height are zero?"
                ],
                to_datetime('2016-07-19 17:38:47.870840'): [
                    to_datetime('2016-07-19 12:45:03.312060'),
                    'nit: |availabilityUrls|'
                ],
                to_datetime('2015-08-24 03:27:11.740570'): [
                    to_datetime('2015-08-24 02:22:15.893870'),
                   '\nIt would be better to use:\n\n  if (!isCurrentlyDisplayed'
                   'InFrame())\n    return nullptr;\n\n'
                ],
                to_datetime('2016-07-19 17:38:47.676770'): [
                    to_datetime('2016-07-19 12:45:03.070610'),
                    'nit: I am probably missing something but could you use '
                    '`m_urls` instead of `data` above?'
                ],
                to_datetime('2016-08-10 23:31:07.938800'): [
                    to_datetime('2016-08-10 23:13:43.472780'),
                    'Please change these to is_worker and is_v8_only.'
                ],
                to_datetime('2015-06-17 19:44:46.019850'): [
                    to_datetime('2015-06-17 19:27:56.248780'),
                    'nit:\n- skia tries to use [] for parameters that are many'
                    '...\n- document scale as 1/determinant ?\n- 1 dst and lots'
                    ' of src params --> (dst, src0, src1, src2)\n\n... '
                    'ComputeInv(SkScaar dst[], const SkScalar src[], SkScalar '
                    'invDet, bool isPersp);'
                ],
                to_datetime('2015-07-31 01:06:50.705140'): [
                    to_datetime('2015-07-30 18:24:22.286210'),
                    "Nit: Just combine this conditional with the one below.  "
                    "You can probably nuke the comment on that since it's just"
                    " restating the code, rather than trying to expand it."
                ],
                to_datetime('2016-07-27 22:06:30.153200'): [
                    to_datetime('2016-07-27 20:44:06.976080'),
                    'This is not proper English :-)'
                ],
                to_datetime('2016-07-20 13:02:10.358540'): [
                    to_datetime('2016-07-19 17:38:47.583740'),
                    "\nWe don't know which URL is valid yet (they all need to "
                    "get passed to the MR to create a sink -> URL map for the "
                    "UI).\n\nI could land a patch to modify the PresentationSe"
                    "rvice and downstream code to support multiple URLs first "
                    "and land this afterwards, but we'd need to modify the "
                    "dispatcher to convert the single URL argument to an "
                    "array.\n\n"
                ],
                to_datetime('2016-08-08 23:53:32.218620'): [
                    to_datetime('2016-08-08 19:01:37.824650'),
                    'This is meant to be setOnKeyDownHandler.'
                ],
                to_datetime('2016-08-08 23:53:30.318460'): [
                    to_datetime('2016-08-08 19:01:37.916060'),
                    'Delegate being an option sounds strange. Pass it '
                    'explicitly.'
                ],
                to_datetime('2016-08-10 23:31:07.987820'): [
                    to_datetime('2016-08-10 23:13:43.599280'),
                    'v8_only_frontend'
                ],
                to_datetime('2016-08-08 23:53:33.174350'): [
                    to_datetime('2016-08-08 19:01:37.730370'),
                    'Can we turn this into a function? Or even a Widget?'
                ],
                to_datetime('2016-07-27 22:06:30.209990'): [
                    to_datetime('2016-07-27 20:44:06.878250'),
                    'style: missing semicolon'
                ],
                to_datetime('2016-07-20 17:20:45.896050'): [
                    to_datetime('2016-07-20 13:02:10.424420'),
                    "\nI'm speechless :)"
                ],
                to_datetime('2016-07-27 22:06:30.310360'): [
                    to_datetime('2016-07-27 20:44:07.033820'),
                    'Unused.'
                ],
                to_datetime('2016-07-20 19:08:20.565100'): [
                    to_datetime('2016-07-20 18:54:57.348360'),
                    'If attachment is GL_DEPTH_STENCIL_ATTACHMENT, framebuffer '
                    'will attach renderbuffer to GL_DEPTH_STENCIL_ATTACHMENT '
                    'here. has_depth_stencil_format check in line 5682 will '
                    'fail though framebuffer has attachment in depth_stencil '
                    'format.'
                ],
                to_datetime('2015-08-31 07:07:02.566860'): [
                    to_datetime('2015-08-28 07:16:49.217320'),
                    'Can we keep the fast loop that combines in 32-bit chunks '
                    'at a time? Then we need to deal with the remaining 1, 2 or'
                    ' 3 bytes at the end. We can then do those one byte at a '
                    'time?'
                ],
                to_datetime('2016-08-11 22:06:23.211340'): [
                    to_datetime('2016-08-10 16:32:25.888370'),
                    'Could you explain git what happened here (for the file in '
                    'a separate change prior to doing this refactoring)'
                ],
                to_datetime('2016-07-22 04:59:44.073440'): [
                    to_datetime('2016-07-22 04:49:03.797020'),
                    'Can you explain why this is safe? I only see this getting'
                    ' used by the tests, so maybe the tests should just bind '
                    'the callback? Or just friend the test so it can bind the '
                    'callback itself?'
                ],
                to_datetime('2016-06-14 00:30:21.156270'): [
                    to_datetime('2016-06-13 18:19:46.679400'),
                    'Since we split this to a separate C++ test fixture, how '
                    'about specifying browserPreload here and remove it from '
                    'https://cs.chromium.org/chromium/src/chrome/test/data/'
                    'webui/settings/dropdown_menu_tests.js?l=11-14.'
                ],
                to_datetime('2015-06-02 10:51:56.838570'): [
                    to_datetime('2015-06-01 15:47:51.045690'),
                    'compatibility_script'
                ],
                to_datetime('2015-08-14 23:57:34.444240'): [
                    to_datetime('2015-08-14 18:40:40.306130'),
                    'requestReload? reloadInspectedPage?'
                ],
                to_datetime('2016-08-11 22:06:23.046620'): [
                    to_datetime('2016-08-10 16:20:29.613320'),
                    'Are there other cases where we might want this?  Maybe '
                    'introduce a new WebInspector.KeyboardShortcut.eventHasCtrl'
                    'OnMac() ?'
                ],
                to_datetime('2016-07-20 19:23:54.083550'): [
                    to_datetime('2016-07-20 19:09:51.162750'),
                    '\nYeah, see GLES2DecoderImpl::DoFramebufferRenderbuffer'
                ],
                to_datetime('2015-08-24 06:52:35.008600'): [
                    to_datetime('2015-08-24 06:28:21.487230'),
                    '\nCan you add a comment on this?\n'
                ],
                to_datetime('2016-07-19 17:38:47.778430'): [
                    to_datetime('2016-07-19 12:45:03.196690'),
                    'We usually put a link on top of the IDL files for '
                    'reference.'
                ],
                to_datetime('2015-08-31 07:07:02.707860'): [
                    to_datetime('2015-08-28 07:16:49.403850'),
                    'o -> object'
                ],
                to_datetime('2016-08-10 23:31:08.082750'): [
                    to_datetime('2016-08-10 23:13:43.652360'),
                    'Revert this one.'
                ],
                to_datetime('2015-06-17 19:44:46.117540'): [
                    to_datetime('2015-06-17 19:27:56.288510'),
                    'why the cast? why not \n\nif (applyingInPlace) {\n    '
                    '*inv = storage;\n}\n'
                ],
                to_datetime('2016-08-08 23:53:30.366890'): [
                    to_datetime('2016-08-08 19:01:37.579210'),
                    'We usually call factory methods createSomething.'
                ],
                to_datetime('2016-07-19 17:38:47.827700'): [
                    to_datetime('2016-07-19 12:45:03.266600'),
                    'I\'m genuinely surprised this is a valid URL :) I would '
                    'expect something like "cast://google.com/?appid=deadbeef".'
                    ' I wonder how "appid=deadbeef" is parsed. Out of curiosity'
                    ', could that be "cast://deadbeef" ? Sounds like the '
                    '"google.com" part isn\'t really needed, is it?'
                ],
                to_datetime('2015-06-02 10:51:56.799960'): [
                    to_datetime('2015-06-01 15:47:51.006490'),
                    'compatibility_script'
                ],
                to_datetime('2016-08-08 23:53:33.490080'): [
                    to_datetime('2016-08-08 19:01:37.684220'),
                    "Let's merge with previous one?"
                ],
                to_datetime('2016-07-20 13:02:10.424420'): [
                    to_datetime('2016-07-19 17:38:47.676770'),
                    '\nWebVector does not provide any method to resize itself '
                    'once allocated.  To populate the vector, the sample code '
                    'suggests using swap().  See:\n\nhttps://cs-staging.'
                    'chromium.org/chromium/src/third_party/WebKit/public/'
                    'platform/WebVector.h?q=WebVector.h&sq=package:chromium&dr'
                    '=CSs'
                ],
                to_datetime('2016-07-20 19:09:51.162750'): [
                    to_datetime('2016-07-20 19:08:20.565100'),
                    "\nActually I think somewhere before reaching here, we "
                    "already split DEPTH_STENCIL into DEPTH and STENCIL. We "
                    "should DCHECK in AttachRenderbuffer or AttachTexture to "
                    "make sure of that, but that's for another CL.  Let me dig "
                    "a bit and find the code."
                ],
                to_datetime('2015-08-27 06:09:53.327470'): [
                    to_datetime('2015-08-21 19:30:30.522240'),
                    "This breaks all cubemap uploads that don't go through one "
                    "of the workarounds, right?\nBecause of the return in line "
                    "1984. We should also avoid the alloc (for |zero|) below "
                    "when not needed."
                ],
                to_datetime('2015-08-31 07:07:02.673750'): [
                    to_datetime('2015-08-28 07:16:49.368620'),
                    'Lift the length checks on x out?\n\nint xlen = x->lenght()'
                    ';\nif (xlen == 0) return other;\n\nand then remove it in '
                    'the two branches?\n\nI think you can do the length '
                    'computation as well since you know they are both '
                    'BaseArrays and that is where you get the length from.'
                ],
                to_datetime('2016-07-11 08:21:00.643720'): [
                    to_datetime('2016-07-08 13:16:37.047520'),
                    'I think you still need to call this against '
                    '`default_prefs_`.'
                ],
                to_datetime('2016-07-19 17:38:47.583740'): [
                    to_datetime('2016-07-19 12:45:03.022090'),
                    'Should this be implemented first? or at least, I think we'
                    ' should have DOMString[] ctor working by taking one URL '
                    'that would be supported (instead of the first in the list)'
                    ' in order to ship.\n\nWhat I would recommend to minimise '
                    'the boilerplate is to pass all the URLs to the service and'
                    ' as soon as we reach the chrome/ layer, pick one and '
                    'ignore all the others.'
                ],
                to_datetime('2016-07-22 07:10:11.899700'): [
                    to_datetime('2016-07-22 06:04:34.144250'),
                    'What does the //base version of this do?\n\nIt seems a '
                    'little unusual that a class outside of //base has to '
                    'reinstall the original listener hook. It seems harder to '
                    'use correctly this way.'
                ],
                to_datetime('2015-08-31 08:50:45.445550'): [
                    to_datetime('2015-08-28 22:41:58.277110'),
                    'Update the version here.'
                ],
                to_datetime('2015-08-14 23:57:34.481470'): [
                    to_datetime('2015-08-14 20:04:31.153440'),
                    'nit: spacing is off.'
                ],
                to_datetime('2015-08-31 07:07:02.444230'): [
                    to_datetime('2015-08-28 07:16:49.095710'),
                    'I think we can share the implementation of length and just'
                    ' have a StringLength native? Lenght is from BaseArray I '
                    'think, so it should be fine to just assert that the '
                    'argument is a OneByteString or a TwoByteString and then '
                    'return BaseArray::cast(object)->length()?'
                ],
                to_datetime('2015-11-20 02:17:07.770870'): [
                    to_datetime('2015-11-19 09:46:25.224900'),
                    "Is `followedRedirect` true for any response that's been "
                    "returned from cache or synthesized via the SW?"
                ],
                to_datetime('2015-07-31 01:06:50.969840'): [
                    to_datetime('2015-07-30 18:24:22.252020'),
                    'Nit: No blank line here'
                ],
                to_datetime('2016-07-15 02:45:29.126760'): [
                    to_datetime('2016-07-15 02:35:50.685400'),
                    "\nHmm, I'm not sure if this translation makes sense. Do "
                    "we really want to actually suspend the tab when receiving"
                    " a critical signal?\n"
                ],
                to_datetime('2016-07-19 17:38:47.733950'): [
                    to_datetime('2016-07-19 12:45:03.151550'),
                    'style: maybe no { } ?'
                ],
                to_datetime('2016-08-11 22:06:23.088580'): [
                    to_datetime('2016-08-10 16:20:29.669980'),
                    'Nit: insert newline above'
                ],
                to_datetime('2016-06-15 05:52:34.142650'): [
                    to_datetime('2016-06-15 02:31:48.914370'),
                    'comment on the point of this'
                ]
            }

        actual = {}
        for c in Comment.objects.exclude(parent=None):
            actual[c.posted] = [c.parent.posted, c.parent.text]

        self.maxDiff = None
        self.assertDictEqual(expected, actual)

        expected = 32
        actual = list(
                Comment.objects.filter(is_useful=True)
                .values_list('text', flat=True)
            )
        self.assertEqual(expected, len(actual))

        expected = [
                'We usually put a link on top of the IDL files for reference.',
                'why the cast? why not \n\nif (applyingInPlace) {\n    *inv = s'
                    'torage;\n}\n',
                "style: we don't use { } when not needed usually.",
                'style: maybe no { } ?', 'nit: |availabilityUrls|',
                'comment on the point of this',
                'Unused.',
                'style: missing semicolon',
                'This was used for autostart modules.',
                'This is not proper English :-)',
                "Nit: Just combine this conditional with the one below.  You ca"
                    "n probably nuke the comment on that since it's just restat"
                    "ing the code, rather than trying to expand it.",
                'Nit: No blank line here', 'nit: spacing is off.',
                'compatibility_script',
                'compatibility_script',
                'Please change these to is_worker and is_v8_only.',
                'Revert this one.',
                'v8_only_frontend',
                'Please change these to is_worker and is_v8_only.',
                'Can we keep the fast loop that combines in 32-bit chunks at a '
                    'time? Then we need to deal with the remaining 1, 2 or 3 by'
                    'tes at the end. We can then do those one byte at a time?',
                'Same comments about length computations.',
                'nit:\n- skia tries to use [] for parameters that are many...\n'
                    '- document scale as 1/determinant ?\n- 1 dst and lots of s'
                    'rc params --> (dst, src0, src1, src2)\n\n... ComputeInv(Sk'
                    'Scaar dst[], const SkScalar src[], SkScalar invDet, bool i'
                    'sPersp);',
                'Update the version here.',
                '\nIt would be better to use:\n\n  if (!isCurrentlyDisplayedInF'
                    'rame())\n    return nullptr;\n\n',
                '\nCan you add a comment on this?\n',
                'I think we can share the implementation of length and just hav'
                    'e a StringLength native? Lenght is from BaseArray I think,'
                    ' so it should be fine to just assert that the argument is '
                    'a OneByteString or a TwoByteString and then return BaseArr'
                    'ay::cast(object)->length()?',
                'o -> object',
                'Is it actually a cancelAutocomplete?',
                'Can we turn this into a function? Or even a Widget?',
                'Delegate being an option sounds strange. Pass it explicitly.',
                'Nit: insert newline above',
                'We usually call factory methods createSomething.'
            ]
        self.assertListEqual(sorted(expected), sorted(actual))

        # Messages
        expected = [
                (
                    to_datetime('2015-07-30 10:40:34.029270'),
                    'frederic.jacob.78@gmail.com',
                    'Code to disconnect the DevTools in kiosk mode. I have put'
                    ' it there because it is the central place for the Devtool'
                    's creation and as such cover all possible case. It work f'
                    'or all OS (Tested it on Win,Osx,Linux) and there are alre'
                    'ady code to disable the Devtools at this place.'
                ),
                (
                    to_datetime('2015-07-30 12:21:22.975630'),
                    'dgozman@chromium.org',
                    'Is it possible to set the policy |prefs::kDevToolsDisable'
                    'd| instead in kiosk mode?'
                ),
                (
                    to_datetime('2015-07-30 18:24:22.393890'),
                    'pkasting@chromium.org',
                    'LGTM'
                ),
                (
                    to_datetime('2015-07-30 23:51:16.478520'),
                    'frederic.jacob.78@gmail.com',
                    '\n\n\nI looked all over the code and I did not saw any place '
                    'that looked good to set\npolicies. I though that it will '
                    'fit in chrome/browser/prefs, but all the policies\nare a '
                    'copy of input flags. Don\'t you think that it could make '
                    'it more difficult\nto associate the disconnection of the '
                    'Devtools with the kiosk mode if we set this \npolicy far '
                    'from the DevTools creation?\n \nDid you have any place in'
                    ' mind where we can set the policy?'
                ),
                (
                    to_datetime('2015-07-30 23:55:34.517080'),
                    'pkasting@chromium.org',
                    'I would not try to set that pref in kiosk mode.  There\'s'
                    ' no real win from doing so (we save one conditional in on'
                    'e place but have to add code to set the pref elsewhere) a'
                    'nd it would make subsequent non-kiosk runs still disable '
                    'the dev tools unless we added even more code to distingui'
                    'sh why the pref was originally set and then unset it.'
                ),
                (
                    to_datetime('2015-07-31 01:06:51.093060'),
                    'frederic.jacob.78@gmail.com',
                    'I removed the comment and merged the two conditions.'
                ),
                (
                    to_datetime('2015-07-31 01:42:57.534600'),
                    'pkasting@chromium.org',
                    'lgtm'
                ),
                (
                    to_datetime('2015-07-31 05:51:11.967330'),
                    'pkasting@chromium.org',
                    'Looks like you need LGTM from a devtools owner.'
                ),
                (

                    to_datetime('2015-07-31 13:46:30.478330'),
                    'dgozman@chromium.org',
                    'lgtm'
                )
            ]

        actual = list(
                Message.objects.filter(review_id=1259853004)
                .values_list('posted', 'sender', 'text')
            )
        self.assertListEqual(sorted(expected), sorted(actual), msg='Data: Message')

        # Tokens
        expected = {
                'I removed the comment and merged the two conditions.': [
                    (1, 'I', 'i', 'i', 'PRP', 'B-NP'),
                    (2, 'removed', 'remov', 'remove', 'VBD', 'B-VP'),
                    (3, 'the', 'the', 'the', 'DT', 'B-NP'),
                    (4, 'comment', 'comment', 'comment', 'NN', 'I-NP'),
                    (5, 'and', 'and', 'and', 'CC', 'O'),
                    (6, 'merged', 'merg', 'merge', 'VBD', 'B-VP'),
                    (7, 'the', 'the', 'the', 'DT', 'B-NP'),
                    (8, 'two', 'two', 'two', 'CD', 'I-NP'),
                    (9, 'conditions', 'condit', 'condition', 'NNS', 'I-NP'),
                    (10, '.', '.', '.', '.', 'O')
                ]
            }

        actual = dict()
        sentences = Sentence.objects.filter(
                message__review_id=1259853004,
                message__posted='2015-07-31 01:06:51.093060'
            )
        for sentence in sentences:
            actual[sentence.text] = list(
                    Token.objects.filter(sentence=sentence)
                    .order_by('position')
                    .values_list(
                        'position', 'token', 'stem', 'lemma', 'pos', 'chunk'
                    )
                )
        self.assertEqual(expected, actual, msg='Data:Token')

        # Materialized View - vw_review_token
        expected = [
                1128633002, 1144393004, 1188433011, 1247623005, 1259853004,
                1286193008, 1292403004, 1293023003, 1295403003, 1299243002,
                1304613003, 1321103002, 1999153002, 2048483002, 2050053002,
                2134723002, 2140383005, 2148643002, 2149523002, 2150783003,
                2151763003, 2177983004, 2189523002, 2211423003, 2230993004
            ]
        actual = list(
                ReviewTokenView.objects.filter(token='lgtm')
                .values_list('review_id', flat=True)
            )
        self.assertCountEqual(expected, actual, msg='Data: vw_review_token')

        # Materialized View - vw_review_lemma
        expected = [
                1259853004, 1292403004, 2150783003, 1286193008, 2177983004,
                2230993004, 1454003003, 2140383005, 1304613003, 2134723002,
                1128633002, 2085023003, 2148643002, 1188433011, 2149523002,
                2050053002, 1144393004, 1999153002, 1293023003, 1295403003,
                2211423003, 1321103002, 2151763003, 1308723003, 1318783003,
                2189523002, 1299243002, 1247623005, 2048483002
            ]
        actual = list(
                ReviewLemmaView.objects.filter(lemma='lgtm')
                .values_list('review_id', flat=True)
            )
        self.assertCountEqual(expected, actual, msg='Data: vw_review_lemma')

    def test_handle_issue_4(self):
        '''Test fix for issue #4

        See https://github.com/andymeneely/sira-nlp/issues/4 for more
        information.
        '''
        with self.settings(YEARS=[2016]):
            call_command('loaddb')

            self.assertFalse(
                    ReviewBug.objects.filter(
                        review__id=2050053002, bug__id=534718
                    ).exists()
                )
            self.assertFalse(
                    ReviewBug.objects.filter(
                        review__id=2048483002, bug__id=545318
                    ).exists()
                )
            self.assertFalse(
                    ReviewBug.objects.filter(
                        review__id=2211423003, bug__id=528486
                    ).exists()
                )

            for model in [Vulnerability, ReviewBug, Review, Bug]:
                model.objects.all().delete()

        with self.settings(YEARS=[2015, 2016]):
            call_command('loaddb')

            self.assertTrue(
                    ReviewBug.objects.filter(
                        review__id=2050053002, bug__id=534718
                    ).exists()
                )
            self.assertTrue(
                    ReviewBug.objects.filter(
                        review__id=2048483002, bug__id=545318
                    ).exists()
                )
            self.assertTrue(
                    ReviewBug.objects.filter(
                        review__id=2211423003, bug__id=528486
                    ).exists()
                )
