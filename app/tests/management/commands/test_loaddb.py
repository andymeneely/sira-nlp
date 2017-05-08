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

    # If there is a way to test whether or not a KeyboardInterrupt is handled
    # correctly, no one on the internet knows how to do it.
    # def test_keyboard_interrupt(self):
    #     p = subprocess.Popen(
    #             ['/home/bsm9339/sira-nlp/manage.py', 'loaddb'],
    #             stderr=subprocess.DEVNULL
    #         )
    #     helpers.sleep(5)
    #     p.send_signal(signal.SIGINT)

    #     self.assertEqual(True, True)

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

        # Messages
        expected = [
                (
                    to_datetime('2015-07-30 10:32:31.936180'),
                    'frederic.jacob.78@gmail.com',
                    'frederic.jacob.78@gmail.com changed reviewers:\n+ dgozman'
                    '@chromium.org, pkasting@google.com'
                ),
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
                    to_datetime('2015-07-30 18:24:22.024440'),
                    'pkasting@chromium.org',
                    'pkasting@chromium.org changed reviewers:\n+ pkasting@chro'
                    'mium.org'
                ),
                (
                    to_datetime('2015-07-30 18:24:22.393890'),
                    'pkasting@chromium.org',
                    'LGTM\n\nNit: No blank line here\n\nNit: Just combine this'
                    ' conditional with the one below.  You can probably nuke t'
                    'he comment on that since it\'s just restating the code, r'
                    'ather than trying to expand it.'
                ),
                (
                    to_datetime('2015-07-30 23:51:16.478520'),
                    'frederic.jacob.78@gmail.com',
                    '\nI looked all over the code and I did not saw any place '
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
                    'I removed the comment and merged the two conditions.\n\nD'
                    'one.\n\nDone.'
                ),
                (
                    to_datetime('2015-07-31 01:42:56.995800'),
                    'pkasting@chromium.org',
                    'The CQ bit was checked by pkasting@chromium.org'
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
                ),
                (
                    to_datetime('2015-07-31 16:30:48.099450'),
                    'pkasting@chromium.org',
                    'The CQ bit was checked by pkasting@chromium.org'
                )
            ]

        actual = list(
                Message.objects.filter(review_id=1259853004)
                .values_list('posted', 'sender', 'text')
            )
        self.assertCountEqual(expected, actual, msg='Data: Message')

        # Tokens
        expected = {
                'frederic.jacob.78@gmail.com changed reviewers:': [
                    (
                        1, 'frederic.jacob.78', 'frederic.jacob.78',
                        'frederic.jacob.78', 'NN'
                    ),
                    (2, '@', '@', '@', 'NNP'),
                    (3, 'gmail.com', 'gmail.com', 'gmail.com', 'NN'),
                    (4, 'changed', 'chang', 'change', 'VBD'),
                    (5, 'reviewers', 'review', 'reviewer', 'NNS'),
                    (6, ':', ':', ':', ':')
                ],
                '+ dgozman@chromium.org, pkasting@google.com': [
                    (1, '+', '+', '+', 'JJ'),
                    (2, 'dgozman', 'dgozman', 'dgozman', 'NN'),
                    (3, '@', '@', '@', 'NNP'),
                    (4, 'chromium.org', 'chromium.org', 'chromium.org', 'NN'),
                    (5, ',', ',', ',', ','),
                    (6, 'pkasting', 'pkast', 'pkasting', 'VBG'),
                    (7, '@', '@', '@', 'CD'),
                    (8, 'google.com', 'google.com', 'google.com', 'NN')
                ]
            }

        actual = dict()
        sentences = Sentence.objects.filter(
                review_id=1259853004,
                message__posted='2015-07-30 10:32:31.936180'
            )
        for sentence in sentences:
            actual[sentence.text] = list(
                    Token.objects.filter(sentence=sentence)
                    .order_by('position')
                    .values_list(
                        'position', 'token', 'stem', 'lemma', 'pos'
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

        # Sentences
#        expected = []
#        actual = list(Sentence.objects.all())
#        print(len(actual))

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
