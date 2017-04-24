import multiprocessing
import os
import signal
import subprocess

from django.conf import settings
from django.db import connections, connection

from app.lib import loaders, taggers
from app.lib.logger import *
from app.models import *
from app import queryStrings as qs
from app.tests import testcases


class QueryStringsTestCase(testcases.SpecialTestCase):
    @classmethod
    def setUpTestData(cls):
        loader = loaders.BugLoader(settings, num_processes=2)
        _ = loader.load()
        loader = loaders.VulnerabilityLoader(settings, num_processes=2)
        _ = loader.load()
        loader = loaders.ReviewLoader(settings, num_processes=2)
        _ = loader.load()
        review_ids = list(Review.objects.all().values_list('id', flat=True))

        tagger = taggers.MissedVulnerabilityTagger(settings, num_processes=2)
        _ = tagger.tag()

        connections.close_all()

        loader = loaders.MessageLoader(
                settings, num_processes=2, review_ids=review_ids
            )
        _ = loader.load()
        loader = loaders.SentenceLoader(
                settings, num_processes=2, review_ids=review_ids
            )
        _ = loader.load()
        loader = loaders.TokenLoader(
                settings, num_processes=2, review_ids=review_ids
            )
        _ = loader.load()

        with connection.cursor() as cursor:
            cursor.execute(
                    'REFRESH MATERIALIZED VIEW {};'.format('vw_review_token')
                )
            cursor.execute(
                    'REFRESH MATERIALIZED VIEW {};'.format('vw_review_lemma')
                )

    def test_queryStrings(self):
        # Sub-Test 1 - query_TF_dict(use_tokens=True)
        expected = [
                {'token': 'starting', 'tf': 1}, {'token': 'Created', 'tf': 1},
                {'token': 'Revert', 'tf': 1}, {'token': 'a', 'tf': 1},
                {'token': 'Simplify', 'tf': 1}, {'token': 'of', 'tf': 1},
                {'token': 'navigation', 'tf': 1}
            ]
        actual = qs.query_TF_dict(1444413002, True)
        self.assertEqual(len(expected), len(list(actual)))
        for entry in expected:
            self.assertTrue(entry in list(actual))

        # Sub-Test 2 - query_TF_dict(use_tokens=False)
        expected = [{'lemma': 'created', 'tf': 1}, {'lemma': 'start', 'tf': 1},
                    {'lemma': 'a', 'tf': 1}, {'lemma': 'revert', 'tf': 1},
                    {'lemma': 'simplify', 'tf': 1},
                    {'lemma': 'navigation', 'tf': 1}, {'lemma': 'of', 'tf': 1}]
        actual = qs.query_TF_dict(1444413002, False)
        self.assertEqual(len(expected), len(list(actual)))
        for entry in expected:
            self.assertTrue(entry in list(actual))

        # Sub-Test 3 - query_DF(use_tokens=True)
        expected = [
                {'token': 'a', 'df': 1}, {'token': 'starting', 'df': 1},
                {'token': 'navigation', 'df': 1}, {'token': 'of', 'df': 1},
                {'token': 'Revert', 'df': 1}, {'token': 'Created', 'df': 1},
                {'token': 'Simplify', 'df': 1}
            ]
        actual = qs.query_DF([1444413002], True)
        self.assertEqual(len(expected), len(list(actual)))
        for entry in expected:
            self.assertTrue(entry in list(actual))

        # Sub-Test 4 - query_DF(use_tokens=False)
        expected = [
                {'df': 1, 'lemma': 'created'}, {'df': 1, 'lemma': 'a'},
                {'df': 1, 'lemma': 'navigation'}, {'df': 1, 'lemma': 'of'},
                {'df': 1, 'lemma': 'start'}, {'df': 1, 'lemma': 'simplify'},
                {'df': 1, 'lemma': 'revert'}
            ]
        actual = qs.query_DF([1444413002], False)
        self.assertEqual(len(expected), len(list(actual)))
        for entry in expected:
            self.assertTrue(entry in list(actual))

        # Sub-Test 5 - query_rIDs_all()
        expected = [1999153002, 2148793002, 12314009, 1295003003, 1304613003,
                    1293023003, 1321103002, 1295403003, 1299243002, 1318783003,
                    1286193008, 1188433011, 1308723003, 1454003003, 1457243002,
                    2027643002, 2148653002, 2148643002, 2140383005, 2149523002,
                    2151613002, 2151763003, 2150783003, 2050053002, 2048483002,
                    2256073002, 2230993004, 2223093002, 1292403004, 1544273002,
                    1259853004, 1128633002, 1144393004, 1247623005, 1444413002,
                    2177983004, 2134723002, 2085023003, 2211423003, 2210603002,
                    2189523002, 2168223002]
        actual = qs.query_rIDs_all()
        self.assertEqual(sorted(expected), sorted(actual))

        # Sub-Test 6 - query_rIDs('all')
        expected = [1999153002, 2148793002, 12314009, 1295003003, 1304613003,
                    1293023003, 1321103002, 1295403003, 1299243002, 1318783003,
                    1286193008, 1188433011, 1308723003, 1454003003, 1457243002,
                    2027643002, 2148653002, 2148643002, 2140383005, 2149523002,
                    2151613002, 2151763003, 2150783003, 2050053002, 2048483002,
                    2256073002, 2230993004, 2223093002, 1292403004, 1544273002,
                    1259853004, 1128633002, 1144393004, 1247623005, 1444413002,
                    2177983004, 2134723002, 2085023003, 2211423003, 2210603002,
                    2189523002, 2168223002]
        actual = qs.query_rIDs('all')
        self.assertEqual(sorted(expected), sorted(actual))

        # Sub-Test 7 - query_rIDs_all()
        expected = expected
        qs.ALL_RIDS = []
        qs.FIXED_RIDS = []
        qs.MISSED_RIDS = []
        qs.NEUTRAL_RIDS = []
        actual = qs.query_rIDs_all()
        self.assertEqual(sorted(expected), sorted(actual))

        # Sub-Test 8 - query_rIDs('missed')
        expected = [1292403004, 1259853004, 1128633002, 1144393004, 1544273002,
                    1247623005, 1444413002, 2177983004, 2134723002, 2085023003,
                    2211423003, 2189523002, 2210603002, 2168223002]
        actual = qs.query_rIDs('missed')
        self.assertEqual(sorted(expected), sorted(actual))

        # Sub-Test 9 - query_rIDs_missed()
        expected = expected
        qs.MISSED_RIDS = []
        actual = qs.query_rIDs_missed()
        self.assertEqual(sorted(expected), sorted(actual))

        # Sub-Test 10 - query_rIDs('fixed')
        expected = [12314009, 1188433011, 1308723003, 1454003003, 1999153002,
                    2027643002, 2177983004, 2223093002]
        actual = qs.query_rIDs('fixed')
        self.assertEqual(sorted(expected), sorted(actual))

        # Sub-Test 11 - query_rIDs_fixed()
        expected = expected
        qs.FIXED_RIDS = []
        actual = qs.query_rIDs_fixed()
        self.assertEqual(sorted(expected), sorted(actual))

        # Sub-Test 12 - query_rIDs('neutral')
        expected = [1293023003, 1299243002, 1295403003, 2150783003, 2151763003,
                    2050053002, 1304613003, 2148793002, 2256073002, 2148643002,
                    2148653002, 2151613002, 2230993004, 1286193008, 1295003003,
                    2149523002, 2048483002, 1321103002, 1318783003, 2140383005,
                    1457243002]
        actual = qs.query_rIDs('neutral')
        self.assertEqual(sorted(expected), sorted(actual))

        # Sub-Test 13 - query_rIDs_neutral()
        expected = expected
        qs.ALL_RIDS = []
        qs.NEUTRAL_RIDS = []
        qs.FIXED_RIDS = []
        qs.MISSED_RIDS = []
        actual = qs.query_rIDs_neutral()
        self.assertEqual(sorted(expected), sorted(actual))

        # Sub-Test 14 - query_rIDs('fm')
        expected = [1454003003, 2223093002, 1444413002, 1259853004, 12314009,
                    2168223002, 2211423003, 2177983004, 2085023003, 1247623005,
                    2210603002, 2189523002, 1999153002, 1128633002, 1544273002,
                    1144393004, 2134723002, 1188433011, 2027643002, 1308723003,
                    1292403004]
        actual = qs.query_rIDs('fm')
        self.assertEqual(sorted(expected), sorted(actual))
        self.assertEqual(sorted(actual), sorted(qs.query_rIDs_fm()))

        # Sub-Test 15 - query_rIDs('nm')
        expected = [2050053002, 1304613003, 1321103002, 1293023003, 1318783003,
                    2140383005, 2150783003, 2085023003, 2211423003, 2168223002,
                    2148793002, 2256073002, 1128633002, 1144393004, 2148643002,
                    2151763003, 2149523002, 2048483002, 1292403004, 2134723002,
                    2189523002, 2148653002, 2151613002, 1259853004, 1444413002,
                    1295003003, 1247623005, 1299243002, 2210603002, 1544273002,
                    2230993004, 1286193008, 1295403003, 1457243002]
        actual = qs.query_rIDs('nm')
        self.assertEqual(sorted(expected), sorted(actual))
        self.assertEqual(sorted(actual), sorted(qs.query_rIDs_nm()))

        # Sub-Test 16 - query_rIDs('nf')
        expected = [2050053002, 1304613003, 2223093002, 12314009, 1321103002,
                    1318783003, 2150783003, 1293023003, 2140383005, 1295403003,
                    2148793002, 2256073002, 2148643002, 1308723003, 1454003003,
                    2151763003, 2149523002, 2048483002, 2148653002, 2151613002,
                    2027643002, 1999153002, 2230993004, 1286193008, 1188433011,
                    1299243002, 1295003003, 1457243002]
        actual = qs.query_rIDs('nf')
        self.assertEqual(sorted(expected), sorted(actual))
        self.assertEqual(sorted(actual), sorted(qs.query_rIDs_nf()))

        # Sub-Test 17 - query_rIDs('2016')
        expected = [1999153002, 2140383005, 2027643002, 2148653002, 2148793002,
                    2148643002, 2151613002, 2151763003, 2149523002, 2050053002,
                    2150783003, 2048483002, 2256073002, 2230993004, 2223093002,
                    2177983004, 2134723002, 2085023003, 2211423003, 2189523002,
                    2210603002, 2168223002]
        actual = qs.query_rIDs('2016')
        self.assertEqual(sorted(expected), sorted(actual))

        # Sub-Test 18 - query_rIDs_year('2016')
        expected = [1999153002, 2140383005, 2027643002, 2148653002, 2148793002,
                    2148643002, 2151613002, 2151763003, 2149523002, 2050053002,
                    2150783003, 2048483002, 2256073002, 2230993004, 2223093002,
                    2177983004, 2134723002, 2085023003, 2211423003, 2189523002,
                    2210603002, 2168223002]
        actual = qs.query_rIDs_year('2016')
        self.assertEqual(sorted(expected), sorted(actual))

        # Sub-Test 15 - query_rIDs_year(<invalid>)
        self.assertRaises(ValueError, qs.query_rIDs_year, '2007')
        self.assertRaises(ValueError, qs.query_rIDs_year, 2008)

        # Sub-Test 19 - query_rIDs_random()
        actual = qs.query_rIDs_all()
        random1 = qs.query_rIDs_random(list(actual), 2)
        random2 = qs.query_rIDs_random(list(actual), 2)
        self.assertNotEqual(sorted(list(random1)), sorted(list(random2)))

        # Sub-Test 21 - query_mIDs('missed')
        expected = 99
        actual = qs.query_mIDs('missed')
        self.assertEqual(expected, len(actual))

        # Sub-Test 22 - query_mIDs_missed()
        expected = 99
        # Force repopulation for unit test coverage.
        qs.MISSED_MIDS = []
        actual = qs.query_mIDs_missed()
        self.assertEqual(expected, len(list(actual)))

        # Sub-Test 23 - query_mIDs('fixed')
        expected = 60
        actual = qs.query_mIDs('fixed')
        self.assertEqual(expected, len(actual))

        # Sub-Test 24 - query_mIDs_fixed()
        expected = 60
        # Force repopulation for unit test coverage.
        qs.FIXED_MIDS = []
        actual = qs.query_mIDs_fixed()
        self.assertEqual(expected, len(list(actual)))

        # Sub-Test 25 - query_mIDs('neutral')
        expected = 238
        actual = qs.query_mIDs('neutral')
        self.assertEqual(expected, len(actual))

        # Sub-Test 26 - query_mIDs_neutral()
        expected = 238
        # Force repopulation for unit test coverage.
        qs.NEUTRAL_MIDS = []
        actual = qs.query_mIDs_neutral()
        self.assertEqual(expected, len(list(actual)))

        # Sub-Test 27 - query_mIDs('fm')
        expected = 152
        actual = qs.query_mIDs('fm')
        self.assertEqual(expected, len(actual))

        # Sub-Test 28 - query_mIDs_fm()
        expected = 152
        # Force repopulation for unit test coverage.
        qs.FM_MIDS = []
        actual = qs.query_mIDs_fm()
        self.assertEqual(expected, len(list(actual)))

        self.assertListEqual(qs.query_mIDs('fm'), qs.query_mIDs_fm())

        # Sub-Test 29 - query_mIDs('nm')
        expected = 330
        actual = qs.query_mIDs('nm')
        self.assertEqual(expected, len(actual))

        # Sub-Test 30 - query_mIDs_nm()
        expected = 330
        # Force repopulation for unit test coverage.
        qs.NM_MIDS = []
        actual = qs.query_mIDs_nm()
        self.assertEqual(expected, len(list(actual)))

        self.assertListEqual(qs.query_mIDs('nm'), qs.query_mIDs_nm())

        # Sub-Test 31 - query_mIDs('nf')
        expected = 291
        actual = qs.query_mIDs('nf')
        self.assertEqual(expected, len(actual))

        # Sub-Test 32 - query_mIDs_nf()
        expected = 291
        # Force repopulation for unit test coverage.
        qs.NF_MIDS = []
        actual = qs.query_mIDs_nf()
        self.assertEqual(expected, len(list(actual)))

        self.assertListEqual(qs.query_mIDs('nf'), qs.query_mIDs_nf())

        # Sub-Test 33 - query_rIDs_year(<invalid>)
        self.assertRaises(ValueError, qs.query_mIDs_year, '2007')
        self.assertRaises(ValueError, qs.query_mIDs_year, 2008)

        # Sub-Test 34 - query_mIDs('2016')
        expected = 235
        actual = qs.query_mIDs('2016')
        self.assertEqual(expected, len(sorted(actual)))
        self.assertEqual(sorted(actual), sorted(qs.query_mIDs_year('2016')))

        # Sub-Test 35 - query_mIDs_random()
        random1 = qs.query_mIDs_random(list(actual), 5)
        random2 = qs.query_mIDs_random(list(actual), 5)
        self.assertNotEqual(sorted(list(random1)), sorted(list(random2)))

        # Sub-Test 36 - query_mIDs_all()
        expected = 390
        actual = qs.query_mIDs_all()
        self.assertEqual(expected, len(sorted(actual)))
        self.assertEqual(sorted(actual), sorted(qs.query_mIDs('all')))

        # Sub-Test 36 - query_mID_text()
        expected = 390
        actual = len(qs.query_mIDs_all())
        self.assertEqual(expected, actual)

        expected = -1
        actual = qs.query_mID_text(999999999999)
        self.assertEqual(expected, actual)

        # Sub-Test 37 - query_tokens()
        data = [2189523002, 2189523002]
        expected = [
                '``', '-', ':', '.', "''", "(", ")", "@", "#", "+", 'after',
                'autostart', 'be', 'bit', 'by', 'change', 'check',
                'chromium.org', '//codereview.chromium.org/2189523002/',
                'comment', 'cq', 'dgozman', 'done', 'english', 'for', 'from',
                'http', 'lcean', 'lgtm', 'l-g-t-m', 'link', 'miss', 'module',
                'not', 'patchset', 'pfeldman', 'proper', 'ps20001', 'ps40001',
                'rebaselined', 'reviewer', 'semicolon', 'send', 'style', 'the',
                'this', 'title', 'to', 'unused', 'upload', 'used', 'with'
            ]
        actual = qs.query_tokens(data, use_tokens=False)
        self.assertEqual(sorted(expected), sorted(actual))

        expected = [
                '``', '-', ':', '.', "''", "(", ")", "@", "#", "+", 'after',
                'autostart', 'bit', 'by', 'changed', 'checked', 'chromium.org',
                '//codereview.chromium.org/2189523002/', 'comments', 'CQ',
                'dgozman', 'Done', 'English', 'for', 'from', 'https', 'is',
                'lcean', 'lgtm', 'l-g-t-m', 'Link', 'missing', 'modules',
                'not', 'patchset', 'pfeldman', 'proper', 'ps20001', 'ps40001',
                'rebaselined', 'reviewers', 'semicolon', 'sent', 'style',
                'the', 'The', 'This', 'title', 'to', 'Unused', 'uploaded',
                'used', 'was', 'with'
            ]
        actual = qs.query_tokens(data, use_tokens=True)
        self.assertEqual(sorted(expected), sorted(actual))

        # Sub-Test 38 - query_tokens_all()
        expected = 1643
        actual = qs.query_tokens_all()
        self.assertEqual(expected, len(list(actual)))

        expected = 2003
        actual = qs.query_tokens_all(True)
        self.assertEqual(expected, len(list(actual)))

        # Sub-Test 39 - query_top_x_tokens()
        data = [2189523002, 2189523002]

        expected = ['chromium.org', 'the', 'be', 'cq', 'to']
        actual = qs.query_top_x_tokens(data, 5)
        self.assertEqual(sorted(expected), sorted(list(actual)))

        expected = ['chromium.org', 'was', 'CQ', 'The', 'Done']
        actual = qs.query_top_x_tokens(data, 5, True)
        self.assertEqual(sorted(expected), sorted(list(actual)))
