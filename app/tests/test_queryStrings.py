import os
import signal
import subprocess

from django.conf import settings
from django.db import connections

from app.lib import loaders
from app.queryStrings import *
from app.tests import testcases


class QueryStringsTestCase(testcases.SpecialTestCase):
    @classmethod
    def setUpTestData(cls):
        loader = loaders.ReviewLoader(settings, num_processes=2)
        _ = loader.load()
        review_ids = list(Review.objects.all().values_list('id', flat=True))
        connections.close_all()
        loader = loaders.MessageLoader(
                settings, num_processes=2, review_ids=review_ids
            )
        _ = loader.load()

'''
    def test_query_TF_dict(self)
        # Sub-Test 1
        expected = [{'token': 'starting', 'tf': 1},
                    {'token': 'Created', 'tf': 1}, {'token': 'Revert', 'tf': 1},
                    {'token': 'a', 'tf': 1}, {'token': 'Simplify', 'tf': 1},
                    {'token': 'of', 'tf': 1}, {'token': 'navigation', 'tf': 1}]
        actual = query_TF_dict(1444413002, False)
        self.assertEqual(len(expected), len(list(actual)))
        for entry in expected:
            self.assertTrue(entry in list(actual))

        # Sub-Test 2
        expected = [{'lemma': 'created', 'tf': 1}, {'lemma': 'start', 'tf': 1},
                    {'lemma': 'a', 'tf': 1}, {'lemma': 'revert', 'tf': 1},
                    {'lemma': 'simplify', 'tf': 1},
                    {'lemma': 'navigation', 'tf': 1}, {'lemma': 'of', 'tf': 1}]
        actual = query_TF_dict(1444413002, True)
        self.assertEqual(len(expected), len(list(actual)))
        for entry in expected:
            self.assertTrue(entry in list(actual))

    def test_query_DF(self):
        # Sub-Test 1
        expected = [{'token': 'a', 'df': 1}, {'token': 'starting', 'df': 1},
                    {'token': 'navigation', 'df': 1}, {'token': 'of', 'df': 1},
                    {'token': 'Revert', 'df': 1}, {'token': 'Created', 'df': 1},
                    {'token': 'Simplify', 'df': 1}]
        actual = query_DF([1444413002], False)
        self.assertEqual(len(expected), len(list(actual)))
        for entry in expected:
            self.assertTrue(entry in list(actual))

        # Sub-Test 2
        expected = [{'df': 1, 'lemma': 'created'}, {'df': 1, 'lemma': 'a'},
                    {'df': 1, 'lemma': 'navigation'}, {'df': 1, 'lemma': 'of'},
                    {'df': 1, 'lemma': 'start'}, {'df': 1, 'lemma': 'simplify'},
                    {'df': 1, 'lemma': 'revert'}]
        actual = query_DF([1444413002], True)
        self.assertEqual(len(expected), len(list(actual)))
        for entry in expected:
            self.assertTrue(entry in list(actual))

    def test_query_rIDs_all(self):
        expected = [1999153002, 2148793002, 12314009, 1295003003, 1304613003,
                    1293023003, 1321103002, 1295403003, 1299243002, 1318783003,
                    1286193008, 1188433011, 1308723003, 1454003003, 1457243002,
                    2027643002, 2148653002, 2148643002, 2140383005, 2149523002,
                    2151613002, 2151763003, 2150783003, 2050053002, 2048483002,
                    2256073002, 2230993004, 2223093002, 1292403004, 1544273002,
                    1259853004, 1128633002, 1144393004, 1247623005, 1444413002,
                    2177983004, 2134723002, 2085023003, 2211423003, 2210603002,
                    2189523002, 2168223002]
        actual = query_rIDs_all()
        self.assertEqual(sorted(expected), sorted(actual))

    def test_query_rIDs(self):
        # Sub-Test 1
        expected = [1999153002, 2148793002, 12314009, 1295003003, 1304613003,
                    1293023003, 1321103002, 1295403003, 1299243002, 1318783003,
                    1286193008, 1188433011, 1308723003, 1454003003, 1457243002,
                    2027643002, 2148653002, 2148643002, 2140383005, 2149523002,
                    2151613002, 2151763003, 2150783003, 2050053002, 2048483002,
                    2256073002, 2230993004, 2223093002, 1292403004, 1544273002,
                    1259853004, 1128633002, 1144393004, 1247623005, 1444413002,
                    2177983004, 2134723002, 2085023003, 2211423003, 2210603002,
                    2189523002, 2168223002]
        actual = query_rIDs('all')
        self.assertEqual(sorted(expected), sorted(actual))
        self.assertEqual(sorted(actual), sorted(query_rIDs_all()))

        # Sub-Test 2
        expected = [1292403004, 1259853004, 1128633002, 1144393004, 1544273002,
                    1247623005, 1444413002, 2177983004, 2134723002, 2085023003,
                    2211423003, 2189523002, 2210603002, 2168223002]
        actual = query_rIDs('missed')
        self.assertEqual(sorted(expected), sorted(actual))
        self.assertEqual(sorted(actual), sorted(query_rIDs_missed()))

        # Sub-Test 3
        expected = [12314009, 1188433011, 1308723003, 1454003003, 1999153002,
                    2027643002, 2177983004, 2223093002]
        actual = query_rIDs('fixed')
        self.assertEqual(sorted(expected), sorted(actual))
        self.assertEqual(sorted(actual), sorted(query_rIDs_fixed()))

        # Sub-Test 4
        expected = [1293023003, 1299243002, 1295403003, 2150783003, 2151763003,
                    2050053002, 1304613003, 2148793002, 2256073002, 2148643002,
                    2148653002, 2151613002, 2230993004, 1286193008, 1295003003,
                    2149523002, 2048483002, 1321103002, 1318783003, 2140383005,
                    1457243002]
        actual = query_rIDs('neutral')
        self.assertEqual(sorted(expected), sorted(actual))
        self.assertEqual(sorted(actual), sorted(query_rIDs_neutral()))

        # Sub-Test 5
        expected = [1454003003, 2223093002, 1444413002, 1259853004, 12314009,
                    2168223002, 2211423003, 2177983004, 2085023003, 1247623005,
                    2210603002, 2189523002, 1999153002, 1128633002, 1544273002,
                    1144393004, 2134723002, 1188433011, 2027643002, 1308723003,
                    1292403004]
        actual = query_rIDs('fm')
        self.assertEqual(sorted(expected), sorted(actual))
        self.assertEqual(sorted(actual), sorted(query_rIDs_fm()))

        # Sub-Test 6
        expected = [2050053002, 1304613003, 1321103002, 1293023003, 1318783003,
                    2140383005, 2150783003, 2085023003, 2211423003, 2168223002,
                    2148793002, 2256073002, 1128633002, 1144393004, 2148643002,
                    2151763003, 2149523002, 2048483002, 1292403004, 2134723002,
                    2189523002, 2148653002, 2151613002, 1259853004, 1444413002,
                    1295003003, 1247623005, 1299243002, 2210603002, 1544273002,
                    2230993004, 1286193008, 1295403003, 1457243002]
        actual = query_rIDs('nm')
        self.assertEqual(sorted(expected), sorted(actual))
        self.assertEqual(sorted(actual), sorted(query_rIDs_nm()))

        # Sub-Test 7
        expected = [2050053002, 1304613003, 2223093002, 12314009, 1321103002,
                    1318783003, 2150783003, 1293023003, 2140383005, 1295403003,
                    2148793002, 2256073002, 2148643002, 1308723003, 1454003003,
                    2151763003, 2149523002, 2048483002, 2148653002, 2151613002,
                    2027643002, 1999153002, 2230993004, 1286193008, 1188433011,
                    1299243002, 1295003003, 1457243002]
        actual = query_rIDs('nf')
        self.assertEqual(sorted(expected), sorted(actual))
        self.assertEqual(sorted(actual), sorted(query_rIDs_nf()))

        # Sub-Test 8
        expected = [1999153002, 2140383005, 2027643002, 2148653002, 2148793002,
                    2148643002, 2151613002, 2151763003, 2149523002, 2050053002,
                    2150783003, 2048483002, 2256073002, 2230993004, 2223093002,
                    2177983004, 2134723002, 2085023003, 2211423003, 2189523002,
                    2210603002, 2168223002]
        actual = query_rIDs('2016')
        self.assertEqual(sorted(expected), sorted(actual))

    def test_query_rIDs_year(self):
        expected = [1999153002, 2140383005, 2027643002, 2148653002, 2148793002,
                    2148643002, 2151613002, 2151763003, 2149523002, 2050053002,
                    2150783003, 2048483002, 2256073002, 2230993004, 2223093002,
                    2177983004, 2134723002, 2085023003, 2211423003, 2189523002,
                    2210603002, 2168223002]
        actual = query_rIDs_year('2016')
        self.assertEqual(sorted(expected), sorted(actual))

        with self.assertRaises(ValueError):
            query_rIDs_year('2007')
            query_rIDs_year(2008)

    def test_query_rIDs_random(self):
        random1 = query_rIDs_random(list(actual), 5)
        random2 = query_rIDs_random(list(actual), 5)
        self.assertNotEqual(sorted(list(random1)), sorted(list(random2)))

    def test_query_mIDs_all(self):
        expected = [53, 54, 55, 56, 57, 58, 59, 61, 62, 63, 64, 60, 65, 66, 67,
                    68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82,
                    83, 84, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162,
                    163, 198, 199, 200, 201, 202, 331, 332, 387, 438, 439, 440,
                    441, 442, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 164,
                    165, 166, 167, 168, 203, 204, 205, 206, 207, 208, 344, 345,
                    346, 347, 348, 349, 350, 395, 396, 397, 398, 399, 96, 97, 98,
                    99, 100, 169, 170, 171, 172, 173, 279, 280, 281, 282, 283,
                    284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295,
                    296, 297, 298, 351, 101, 102, 103, 104, 105, 106, 107, 108,
                    109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120,
                    174, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 121,
                    122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133,
                    134, 135, 136, 177, 178, 179, 180, 181, 182, 183, 184, 185,
                    186, 238, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146,
                    147, 148, 149, 150, 151, 152, 175, 176, 209, 210, 211, 212,
                    239, 302, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196,
                    197, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343,
                    388, 389, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222,
                    223, 277, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233,
                    234, 235, 236, 237, 240, 241, 242, 243, 244, 245, 278, 300,
                    246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257,
                    299, 301, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267,
                    268, 269, 270, 271, 272, 273, 274, 275, 276, 303, 304, 305,
                    306, 307, 308, 309, 352, 353, 354, 355, 356, 357, 358, 359,
                    360, 361, 362, 363, 364, 408, 409, 410, 411, 412, 413, 414,
                    415, 416, 417, 418, 419, 310, 311, 312, 313, 374, 375, 376,
                    377, 378, 379, 429, 430, 431, 432, 433, 434, 435, 436, 437,
                    324, 325, 326, 327, 328, 329, 330, 380, 381, 382, 383, 384,
                    385, 386, 365, 366, 367, 368, 369, 370, 371, 372, 373, 420,
                    421, 422, 423, 424, 425, 426, 427, 428, 390, 391, 392, 393,
                    394, 400, 401, 402, 403, 404, 405, 406, 407]
        actual = query_mIDs_all()
        self.assertEqual(sorted(expected), sorted(actual))

    def test_query_mIDs(self):
        # Sub-Test 1
        expected = [53, 54, 55, 56, 57, 58, 59, 61, 62, 63, 64, 60, 65, 66, 67,
                    68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82,
                    83, 84, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162,
                    163, 198, 199, 200, 201, 202, 331, 332, 387, 438, 439, 440,
                    441, 442, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 164,
                    165, 166, 167, 168, 203, 204, 205, 206, 207, 208, 344, 345,
                    346, 347, 348, 349, 350, 395, 396, 397, 398, 399, 96, 97, 98,
                    99, 100, 169, 170, 171, 172, 173, 279, 280, 281, 282, 283,
                    284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295,
                    296, 297, 298, 351, 101, 102, 103, 104, 105, 106, 107, 108,
                    109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120,
                    174, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 121,
                    122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133,
                    134, 135, 136, 177, 178, 179, 180, 181, 182, 183, 184, 185,
                    186, 238, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146,
                    147, 148, 149, 150, 151, 152, 175, 176, 209, 210, 211, 212,
                    239, 302, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196,
                    197, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343,
                    388, 389, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222,
                    223, 277, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233,
                    234, 235, 236, 237, 240, 241, 242, 243, 244, 245, 278, 300,
                    246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257,
                    299, 301, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267,
                    268, 269, 270, 271, 272, 273, 274, 275, 276, 303, 304, 305,
                    306, 307, 308, 309, 352, 353, 354, 355, 356, 357, 358, 359,
                    360, 361, 362, 363, 364, 408, 409, 410, 411, 412, 413, 414,
                    415, 416, 417, 418, 419, 310, 311, 312, 313, 374, 375, 376,
                    377, 378, 379, 429, 430, 431, 432, 433, 434, 435, 436, 437,
                    324, 325, 326, 327, 328, 329, 330, 380, 381, 382, 383, 384,
                    385, 386, 365, 366, 367, 368, 369, 370, 371, 372, 373, 420,
                    421, 422, 423, 424, 425, 426, 427, 428, 390, 391, 392, 393,
                    394, 400, 401, 402, 403, 404, 405, 406, 407]
        actual = query_mIDs('all')
        self.assertEqual(sorted(expected), sorted(actual))
        self.assertEqual(sorted(actual), sorted(query_mIDs_all()))

        # Sub-Test 2
        expected = [344, 345, 346, 347, 348, 349, 350, 395, 396, 397, 398, 399,
                    400, 401, 402, 403, 365, 366, 388, 389, 390, 391, 392, 393,
                    394, 380, 381, 382, 383, 384, 385, 371, 372, 373, 374, 375,
                    376, 377, 378, 379, 429, 430, 431, 432, 433, 434, 435, 436,
                    437, 387, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360,
                    361, 362, 363, 404, 405, 406, 407, 364, 408, 409, 410, 411,
                    412, 413, 414, 415, 416, 367, 368, 369, 370, 417, 418, 419,
                    420, 421, 422, 423, 424, 425, 426, 427, 428, 386, 438, 439,
                    440, 441, 442]
        actual = query_mIDs('missed')
        self.assertEqual(sorted(expected), sorted(actual))
        self.assertEqual(sorted(actual), sorted(list(query_mIDs_missed())))

        # Sub-Test 3
        expected = query_mIDs_fixed()
        actual = query_mIDs('fixed')
        self.assertEqual(sorted(expected), sorted(actual))

        # Sub-Test 4
        expected = query_mIDs_neutral()
        actual = query_mIDs('neutral')
        self.assertEqual(sorted(expected), sorted(actual))

        # Sub-Test 5
        expected = query_mIDs_fm()
        actual = query_mIDs('fm')
        self.assertEqual(sorted(expected), sorted(actual))

        # Sub-Test 6
        expected = query_mIDs_nm()
        actual = query_mIDs('nm')
        self.assertEqual(sorted(expected), sorted(actual))

        # Sub-Test 7
        expected = query_mIDs_nf()
        actual = query_mIDs('nf')
        self.assertEqual(sorted(expected), sorted(actual))

    def test_query_mIDs_year(self):
        expected = list(query_mIDs_year('2016'))
        actual = query_mIDs('2016')
        self.assertEqual(sorted(expected), sorted(list(actual)))

        with self.assertRaises(ValueError):
            query_mIDs_year('2007')
            query_mIDs_year(2008)

    def test_query_mIDs_random(self):
        random1 = query_mIDs_random(list(actual), 5)
        random2 = query_mIDs_random(list(actual), 5)
        self.assertNotEqual(sorted(list(random1)), sorted(list(random2)))
'''
