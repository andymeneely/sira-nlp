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

        loader = loaders.MessageLoader(settings, num_processes=2, review_ids=review_ids)
        _ = loader.load()
        loader = loaders.TokenLoader(settings, num_processes=2, review_ids=review_ids)
        _ = loader.load()

        with connection.cursor() as cursor:
            cursor.execute('REFRESH MATERIALIZED VIEW {};'.format('vw_review_token'))
            cursor.execute('REFRESH MATERIALIZED VIEW {};'.format('vw_review_lemma'))

    def test_queryStrings(self):
        # Sub-Test 1 - query_TF_dict(use_tokens=True)
        expected = [{'token': 'starting', 'tf': 1},
                    {'token': 'Created', 'tf': 1}, {'token': 'Revert', 'tf': 1},
                    {'token': 'a', 'tf': 1}, {'token': 'Simplify', 'tf': 1},
                    {'token': 'of', 'tf': 1}, {'token': 'navigation', 'tf': 1}]
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
        expected = [{'token': 'a', 'df': 1}, {'token': 'starting', 'df': 1},
                    {'token': 'navigation', 'df': 1}, {'token': 'of', 'df': 1},
                    {'token': 'Revert', 'df': 1}, {'token': 'Created', 'df': 1},
                    {'token': 'Simplify', 'df': 1}]
        actual = qs.query_DF([1444413002], True)
        self.assertEqual(len(expected), len(list(actual)))
        for entry in expected:
            self.assertTrue(entry in list(actual))

        # Sub-Test 4 - query_DF(use_tokens=False)
        expected = [{'df': 1, 'lemma': 'created'}, {'df': 1, 'lemma': 'a'},
                    {'df': 1, 'lemma': 'navigation'}, {'df': 1, 'lemma': 'of'},
                    {'df': 1, 'lemma': 'start'}, {'df': 1, 'lemma': 'simplify'},
                    {'df': 1, 'lemma': 'revert'}]
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

        # Sub-Test 20 - query_rIDs_empty()
        expected = [12314009, 12314009, 1293023003, 1293023003, 1293023003,
                    1293023003, 1304613003, 1304613003, 1304613003, 1304613003,
                    1304613003, 1304613003, 1304613003, 1304613003, 1304613003,
                    1304613003, 1304613003, 1295003003, 1295003003, 1295003003,
                    1295003003, 1295403003, 1295403003, 1295403003, 1295403003,
                    1295403003, 1295403003, 1286193008, 1286193008, 1286193008,
                    1286193008, 1286193008, 1286193008, 1286193008, 1286193008,
                    1286193008, 1286193008, 1286193008, 1286193008, 1286193008,
                    1286193008, 1286193008, 1286193008, 1286193008, 1286193008,
                    1286193008, 1286193008, 1321103002, 1321103002, 1321103002,
                    1321103002, 1318783003, 1318783003, 1318783003, 1318783003,
                    1318783003, 1308723003, 1308723003, 1308723003, 1308723003,
                    1308723003, 1308723003, 1308723003, 1308723003, 1308723003,
                    1308723003, 1308723003, 1308723003, 1308723003, 1308723003,
                    1308723003, 1308723003, 1292403004, 1292403004, 1292403004,
                    1292403004, 1299243002, 1299243002, 1299243002, 1299243002,
                    1299243002, 1299243002, 1299243002, 1299243002, 1299243002,
                    1299243002, 1299243002, 1188433011, 1188433011, 1188433011,
                    1188433011, 1188433011, 1188433011, 1188433011, 1188433011,
                    1188433011, 1188433011, 1188433011, 1188433011, 1454003003,
                    1454003003, 1454003003, 1454003003, 1454003003, 1454003003,
                    1454003003, 1454003003, 1454003003, 1454003003, 1454003003,
                    1259853004, 1259853004, 1259853004, 1259853004, 1259853004,
                    1259853004, 1259853004, 1259853004, 1259853004, 1259853004,
                    1259853004, 1259853004, 1259853004, 1128633002, 1128633002,
                    1128633002, 1128633002, 1128633002, 1128633002, 1247623005,
                    1247623005, 1247623005, 1247623005, 1247623005, 1247623005,
                    1247623005, 1444413002, 2027643002, 2027643002, 2027643002,
                    2148643002, 2148643002, 1292403004, 1292403004, 1292403004,
                    1544273002, 1144393004, 1144393004, 1144393004, 1144393004,
                    1144393004, 1144393004, 1144393004, 1144393004, 1144393004,
                    1457243002, 1457243002, 1457243002, 1457243002, 1457243002,
                    1999153002, 1999153002, 1999153002, 1999153002, 1999153002,
                    2148643002, 2148643002, 2148643002, 2148643002, 2148643002,
                    2148643002, 2148643002, 2027643002, 2027643002, 2140383005,
                    2140383005, 2140383005, 2140383005, 2140383005, 2140383005,
                    2140383005, 2140383005, 2140383005, 2140383005, 2140383005,
                    2148653002, 2148653002, 2148793002, 2149523002, 2230993004,
                    2148643002, 2149523002, 2149523002, 2149523002, 2149523002,
                    2149523002, 2149523002, 2149523002, 2151613002, 2151613002,
                    2151613002, 2151613002, 2151613002, 2150783003, 2150783003,
                    2150783003, 2150783003, 2150783003, 2150783003, 2150783003,
                    2150783003, 2150783003, 2150783003, 2150783003, 2150783003,
                    2150783003, 2150783003, 2150783003, 2150783003, 2150783003,
                    2150783003, 2150783003, 2150783003, 2150783003, 2150783003,
                    2150783003, 2150783003, 2150783003, 2230993004, 2149523002,
                    2149523002, 2149523002, 2149523002, 2149523002, 2149523002,
                    2149523002, 2149523002, 2149523002, 2149523002, 2149523002,
                    2149523002, 2149523002, 2149523002, 2149523002, 2149523002,
                    2149523002, 2149523002, 2149523002, 2149523002, 2149523002,
                    2149523002, 2149523002, 2149523002, 2149523002, 2149523002,
                    2149523002, 2230993004, 2149523002, 2149523002, 2149523002,
                    2149523002, 2149523002, 2149523002, 2149523002, 2230993004,
                    2149523002, 2149523002, 2149523002, 2149523002, 2149523002,
                    2149523002, 2149523002, 2149523002, 2149523002, 2149523002,
                    2149523002, 2149523002, 2149523002, 2149523002, 2149523002,
                    2149523002, 2230993004, 2230993004, 2149523002, 2149523002,
                    2149523002, 2149523002, 2149523002, 2149523002, 2149523002,
                    2149523002, 2149523002, 2149523002, 2149523002, 2149523002,
                    2151763003, 2151763003, 2151763003, 2151763003, 2151763003,
                    2151763003, 2050053002, 2050053002, 2050053002, 2050053002,
                    2050053002, 2050053002, 2050053002, 2050053002, 2230993004,
                    2150783003, 2150783003, 2150783003, 2150783003, 2150783003,
                    2150783003, 2048483002, 2048483002, 2048483002, 2048483002,
                    2177983004, 2177983004, 2177983004, 2177983004, 2177983004,
                    2177983004, 2177983004, 2134723002, 2134723002, 2134723002,
                    2134723002, 2134723002, 2134723002, 2134723002, 2134723002,
                    2134723002, 2230993004, 2230993004, 2230993004, 2230993004,
                    2050053002, 2050053002, 2050053002, 2050053002, 2050053002,
                    2050053002, 2050053002, 2050053002, 2050053002, 2085023003,
                    2085023003, 2085023003, 2085023003, 2223093002, 2223093002,
                    2211423003, 2211423003, 2211423003, 2211423003, 2211423003,
                    2211423003, 2211423003, 2211423003, 2211423003, 2211423003,
                    2211423003, 2211423003, 2189523002, 2189523002, 2189523002,
                    2189523002, 2189523002, 2189523002, 2189523002, 2189523002,
                    2189523002, 2210603002, 2210603002, 2210603002, 2210603002,
                    2210603002, 2210603002, 2210603002, 2210603002, 2210603002,
                    2168223002, 2168223002, 2168223002, 2168223002, 2168223002]
        actual = qs.query_rIDs_empty()
        self.assertEqual(sorted(expected), sorted(actual))

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
        expected = [1221, 1222, 1223, 1224, 1225, 1226, 1227, 1228, 1229, 1230,
                    1231, 1232, 1233, 1234, 1235, 1236, 1237, 1238, 1239, 1240,
                    1241, 1242, 1243, 1244, 1245, 1246, 1247, 1248, 1249, 1250,
                    1251, 1252, 1253, 1254, 1255, 1256, 1257, 1258, 1259, 1260,
                    1261, 1262, 1263, 1264, 1265, 1266, 1267, 1268, 1269, 1270,
                    1271, 1272, 1273, 1274, 1275, 1276, 1277, 1278, 1279, 1280,
                    1281, 1282, 1283, 1284, 1285, 1286, 1287, 1288, 1289, 1290,
                    1291, 1292, 1293, 1294, 1295, 1296, 1297, 1298, 1299, 1300,
                    1301, 1302, 1303, 1304, 1305, 1306, 1307, 1308, 1309, 1310,
                    1311, 1312, 1313, 1314, 1315, 1316, 1317, 1318, 1319, 1320,
                    1321, 1322, 1323, 1324, 1325, 1326, 1327, 1328, 1329, 1330,
                    1331, 1332, 1333, 1334, 1335, 1336, 1337, 1338, 1339, 1340,
                    1341, 1342, 1343, 1344, 1345, 1346, 1347, 1348, 1349, 1350,
                    1351, 1352, 1353, 1354, 1355, 1356, 1357, 1358, 1359, 1360,
                    1361, 1362, 1363, 1364, 1365, 1366, 1367, 1368, 1369, 1370,
                    1371, 1372, 1373, 1374, 1375, 1376, 1377, 1378, 1379, 1380,
                    1381, 1382, 1383, 1384, 1385, 1386, 1387, 1388, 1389, 1390,
                    1391, 1392, 1393, 1394, 1395, 1396, 1397, 1398, 1399, 1400,
                    1401, 1402, 1403, 1404, 1405, 1406, 1407, 1408, 1409, 1410,
                    1411, 1412, 1413, 1414, 1415, 1416, 1417, 1418, 1419, 1420,
                    1421, 1422, 1423, 1424, 1425, 1426, 1427, 1428, 1429, 1430,
                    1431, 1432, 1433, 1434, 1435, 1436, 1437, 1438, 1439, 1440,
                    1441, 1442, 1443, 1444, 1445, 1446, 1447, 1448, 1449, 1450,
                    1451, 1452, 1453, 1454, 1455]
        actual = qs.query_mIDs('2016')
        self.assertEqual(sorted(expected), sorted(actual))
        self.assertEqual(sorted(actual), sorted(qs.query_mIDs_year('2016')))

        # Sub-Test 35 - query_mIDs_random()
        random1 = qs.query_mIDs_random(list(actual), 5)
        random2 = qs.query_mIDs_random(list(actual), 5)
        self.assertNotEqual(sorted(list(random1)), sorted(list(random2)))

        # Sub-Test 36 - query_mIDs_all()
        expected = [1066, 1067, 1068, 1069, 1070, 1071, 1072, 1073, 1074, 1075,
                    1076, 1077, 1078, 1079, 1080, 1081, 1082, 1083, 1084, 1085,
                    1086, 1087, 1088, 1089, 1090, 1091, 1092, 1093, 1094, 1095,
                    1096, 1097, 1098, 1099, 1100, 1101, 1102, 1103, 1104, 1105,
                    1106, 1107, 1108, 1109, 1110, 1111, 1112, 1113, 1114, 1115,
                    1116, 1117, 1118, 1119, 1120, 1121, 1122, 1123, 1124, 1125,
                    1126, 1127, 1128, 1129, 1130, 1131, 1132, 1133, 1134, 1135,
                    1136, 1137, 1138, 1139, 1140, 1141, 1142, 1143, 1144, 1145,
                    1146, 1147, 1148, 1149, 1150, 1151, 1152, 1153, 1154, 1155,
                    1156, 1157, 1158, 1159, 1160, 1161, 1162, 1163, 1164, 1165,
                    1166, 1167, 1168, 1169, 1170, 1171, 1172, 1173, 1174, 1175,
                    1176, 1177, 1178, 1179, 1180, 1181, 1182, 1183, 1184, 1185,
                    1186, 1187, 1188, 1189, 1190, 1191, 1192, 1193, 1194, 1195,
                    1196, 1197, 1198, 1199, 1200, 1201, 1202, 1203, 1204, 1205,
                    1206, 1207, 1208, 1209, 1210, 1211, 1212, 1213, 1214, 1215,
                    1216, 1217, 1218, 1219, 1220, 1221, 1222, 1223, 1224, 1225,
                    1226, 1227, 1228, 1229, 1230, 1231, 1232, 1233, 1234, 1235,
                    1236, 1237, 1238, 1239, 1240, 1241, 1242, 1243, 1244, 1245,
                    1246, 1247, 1248, 1249, 1250, 1251, 1252, 1253, 1254, 1255,
                    1256, 1257, 1258, 1259, 1260, 1261, 1262, 1263, 1264, 1265,
                    1266, 1267, 1268, 1269, 1270, 1271, 1272, 1273, 1274, 1275,
                    1276, 1277, 1278, 1279, 1280, 1281, 1282, 1283, 1284, 1285,
                    1286, 1287, 1288, 1289, 1290, 1291, 1292, 1293, 1294, 1295,
                    1296, 1297, 1298, 1299, 1300, 1301, 1302, 1303, 1304, 1305,
                    1306, 1307, 1308, 1309, 1310, 1311, 1312, 1313, 1314, 1315,
                    1316, 1317, 1318, 1319, 1320, 1321, 1322, 1323, 1324, 1325,
                    1326, 1327, 1328, 1329, 1330, 1331, 1332, 1333, 1334, 1335,
                    1336, 1337, 1338, 1339, 1340, 1341, 1342, 1343, 1344, 1345,
                    1346, 1347, 1348, 1349, 1350, 1351, 1352, 1353, 1354, 1355,
                    1356, 1357, 1358, 1359, 1360, 1361, 1362, 1363, 1364, 1365,
                    1366, 1367, 1368, 1369, 1370, 1371, 1372, 1373, 1374, 1375,
                    1376, 1377, 1378, 1379, 1380, 1381, 1382, 1383, 1384, 1385,
                    1386, 1387, 1388, 1389, 1390, 1391, 1392, 1393, 1394, 1395,
                    1396, 1397, 1398, 1399, 1400, 1401, 1402, 1403, 1404, 1405,
                    1406, 1407, 1408, 1409, 1410, 1411, 1412, 1413, 1414, 1415,
                    1416, 1417, 1418, 1419, 1420, 1421, 1422, 1423, 1424, 1425,
                    1426, 1427, 1428, 1429, 1430, 1431, 1432, 1433, 1434, 1435,
                    1436, 1437, 1438, 1439, 1440, 1441, 1442, 1443, 1444, 1445,
                    1446, 1447, 1448, 1449, 1450, 1451, 1452, 1453, 1454, 1455]
        actual = qs.query_mIDs_all()
        self.assertEqual(sorted(expected), sorted(actual))
        self.assertEqual(sorted(actual), sorted(qs.query_mIDs('all')))

        # Sub-Test 36 - query_mID_text()
        expected = "The CQ bit was checked by pfeldman@chromium.org"
        actual = qs.query_mID_text(1446)
        self.assertEqual(expected, actual)

        expected = -1
        actual = qs.query_mID_text(999999999999)
        self.assertEqual(expected, actual)

        # Sub-Test 37 - query_tokens()
        data = [2189523002, 2189523002]
        expected = ['``', '-', ':', '.', "''", "(", ")", "@", "#", "+", 'after',
                    'autostart', 'be', 'bit', 'by', 'change', 'check',
                    'chromium.org', '//codereview.chromium.org/2189523002/',
                    'comment', 'cq', 'dgozman', 'done', 'english', 'for', 'from',
                    'http', 'lcean', 'lgtm', 'l-g-t-m', 'link', 'miss', 'module',
                    'not', 'patchset', 'pfeldman', 'proper', 'ps20001',
                    'ps40001', 'rebaselined', 'reviewer', 'semicolon', 'send',
                    'style', 'the', 'this', 'title', 'to', 'unused', 'upload',
                    'used', 'with']
        actual = qs.query_tokens(data, use_tokens=False)
        self.assertEqual(sorted(expected), sorted(actual))

        expected = ['``', '-', ':', '.', "''", "(", ")", "@", "#", "+", 'after',
                    'autostart', 'bit', 'by', 'changed', 'checked',
                    'chromium.org', '//codereview.chromium.org/2189523002/',
                    'comments', 'CQ', 'dgozman', 'Done', 'English', 'for',
                    'from', 'https', 'is', 'lcean', 'lgtm', 'l-g-t-m', 'Link',
                    'missing', 'modules', 'not', 'patchset', 'pfeldman',
                    'proper', 'ps20001', 'ps40001', 'rebaselined', 'reviewers',
                    'semicolon', 'sent', 'style', 'the', 'The', 'This', 'title',
                    'to', 'Unused', 'uploaded', 'used', 'was', 'with']
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
