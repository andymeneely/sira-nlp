import csv
import os
import tempfile

from collections import OrderedDict

from django.conf import settings
from django.test import TestCase

from app.lib import files


class FilesTestCase(TestCase):
    def setUp(self):
        self.files = files.Files(settings)

    def test_get_bugs(self):
        expected = [
                '606056', '610176', '627655', '602509', '584783', '628496',
                '624894', '617492', '609260', '613160', '625357', '628110',
                '576270', '620126', '607690', '583485', '636539', '613918',
                '619379', '626102', '642598'
            ]
        actual = self.files.get_bugs(year=2016)

        self.assertCountEqual(expected, [item['id'] for item in actual])

    def test_get_bugs_path(self):
        expected = self.files.bugs_path.format(year=2016)

        self.assertEqual(expected, self.files.get_bugs_path(year=2016))

    def test_get_ids_path(self):
        expected = self.files.ids_path.format(switch='reviews')

        self.assertEqual(expected, self.files.get_ids_path(switch='reviews'))

    def test_get_ids(self):
        expected = [
                '2148653002', '2150783003', '2140383005', '2148643002',
                '2149523002', '2151763003', '2148793002', '2151613002',
                '2027643002', '1999153002', '2050053002', '2048483002',
                '2177983004', '2134723002', '2189523002', '2168223002',
                '2223093002', '2085023003', '2256073002', '2210603002',
                '2230993004', '2211423003'
            ]

        actual = self.files.get_ids(year=2016, switch='reviews')

        self.assertCountEqual(expected, actual)

    def test_get_messages(self):
        expected = [
                (
                    'ochang@chromium.org',
                    'Description was changed from\n\n==========\nRoll PDFium 8'
                    'b45eb1..3cbb6fb\n\nhttps://pdfium.googlesource.com/pdfium'
                    '.git/+log/8b45eb1..3cbb6fb\n\nBUG=613160\n\nTEST=bots\n=='
                    '========\n\nto\n\n==========\nRoll PDFium 8b45eb1..3cbb6f'
                    'b\n\nhttps://pdfium.googlesource.com/pdfium.git/+log/8b45'
                    'eb1..3cbb6fb\n\nBUG=613160\nTBR=thestig@chromium.org\n==='
                    '======='
                ),
                (
                    'ochang@chromium.org',
                    'ochang@chromium.org changed reviewers:\n+ thestig@chromiu'
                    'm.org'
                ),
                (
                    'ochang@chromium.org',
                    'TBR'
                ),
                (
                    'ochang@chromium.org',
                    'The CQ bit was checked by ochang@chromium.org'
                ),
                (
                    'thestig@chromium.org',
                    'lgtm'
                )
            ]

        actual = self.files.get_messages(id=1999153002, year=2016, clean=False)

        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected, actual)

    def test_get_description(self):
        expected = (
                'Roll PDFium 8b45eb1..3cbb6fb\n\nhttps://pdfium.googlesource.c'
                'om/pdfium.git/+log/8b45eb1..3cbb6fb\n\nBUG=613160\nTBR=thesti'
                'g@chromium.org\n\nCommitted: https://crrev.com/3a89e0aab29ceb'
                'cfe1f559387215c4b10be86b76\nCr-Commit-Position: refs/heads/ma'
                'ster@{#395117}'
            )

        actual = self.files.get_description(id=1999153002, year=2016)

        self.assertEqual(expected, actual)

    def test_get_review(self):
        actual = self.files.get_review(id=1999153002, year=2016)

        self.assertTrue(type(actual) is dict)
        self.assertEqual(1999153002, actual['issue'])

    def test_get_review_nonexistent(self):
        with self.assertRaises(Exception):
            self.files.get_review(id=1999153000, year=2016)

    def test_get_reviews(self):
        expected = [
                1999153002, 2027643002, 2140383005, 2148643002, 2148653002,
                2148793002, 2149523002, 2150783003, 2151613002, 2151763003,
                2050053002, 2048483002, 2177983004, 2134723002, 2189523002,
                2168223002, 2223093002, 2085023003, 2256073002, 2210603002,
                2230993004, 2211423003
            ]

        actual = [
                review['issue'] for review in self.files.get_reviews(year=2016)
            ]

        self.assertCountEqual(expected, actual)

    def test_get_vulnerabilities(self):
        expected = [
                ('blog', 'CVE-2016-5165', '618037'),
                ('manual', 'CVE-2016-2845', '542060'),
                ('manual', 'CVE-2013-0908', '174059')
            ]

        actual = self.files.get_vulnerabilities()

        self.assertCountEqual(expected, actual)

    def test_get_year(self):
        expected = '2016'

        actual = self.files.get_year(id=1999153002, switch='reviews')

        self.assertEqual(expected, actual)

    def test_get_year_nonexistent(self):
        with self.assertRaises(Exception):
            self.files.get_year(id=1999153000, switch='reviews')

    def test_save_ids(self):
        data = list(range(100001, 100010))
        expected = [str(item) for item in data]

        with tempfile.TemporaryDirectory() as tempdir:
            with self.settings(IDS_PATH=os.path.join('/tmp', tempdir)):
                f = files.Files(settings)
                f.save_ids(year=9999, ids=data, switch='reviews')
                path = os.path.join('/tmp', tempdir, '9999.csv')

                self.assertTrue(os.path.exists(path))
                actual = None
                with open(path, 'r') as file:
                    reader = csv.reader(file)
                    actual = [row[0] for row in reader]
                self.assertCountEqual(expected, actual)

    def test_save_reviews(self):
        data = [{'issue': id} for id in range(100001, 100010)]
        expected = data

        with tempfile.TemporaryDirectory() as tempdir:
            with self.settings(
                    REVIEWS_PATH=os.path.join('/tmp', tempdir, '{year}')
                 ):
                f = files.Files(settings)
                f.save_reviews(year=9999, chunk=1, reviews=data, errors=None)
                path = os.path.join('/tmp', tempdir, '9999')
                self.assertTrue(os.path.exists(path))
                path = os.path.join('/tmp', tempdir, '9999', 'reviews.1.json')
                self.assertTrue(os.path.exists(path))

                actual = f.get_reviews(year=9999)
                self.assertCountEqual(expected, actual)

    def test_stat_review(self):
        expected = {
                'status': 'Closed', 'created': '2016-05-20 17:03:11.225970',
                'reviewers': 1, 'messages': 10, 'patchsets': 1
            }

        actual = self.files.stat_review(id=1999153002)

        self.assertEqual(expected, actual)

    def test_stat_reviews(self):
        expected = {
                'reviews': 22, 'open': 2,
                'messages': OrderedDict([
                    (2149523002, 92), (2150783003, 56), (2140383005, 25),
                    (2211423003, 24), (2050053002, 21), (2230993004, 20),
                    (2189523002, 19), (2148643002, 16), (2168223002, 14),
                    (2177983004, 13), (2134723002, 13), (2151613002, 11),
                    (1999153002, 10), (2151763003, 10), (2210603002, 9),
                    (2027643002, 8), (2085023003, 8), (2048483002, 8),
                    (2148653002, 4), (2148793002, 4), (2223093002, 2),
                    (2256073002, 0)
                ]),
                'patchsets': OrderedDict([
                    (2149523002, 7), (2150783003, 7), (2140383005, 7),
                    (2210603002, 6), (2148643002, 6), (2050053002, 4),
                    (2168223002, 3), (2189523002, 3), (2177983004, 3),
                    (2230993004, 3), (2134723002, 2), (2211423003, 2),
                    (2048483002, 2), (2151613002, 1), (2148653002, 1),
                    (2027643002, 1), (2085023003, 1), (2223093002, 1),
                    (2256073002, 1), (1999153002, 1), (2151763003, 1),
                    (2148793002, 1)
                ]),
                'comments': OrderedDict([
                    (2210603002, 20), (2148643002, 20), (2149523002, 19),
                    (2189523002, 8), (2230993004, 8), (2050053002, 6),
                    (2150783003, 6), (2134723002, 2), (2168223002, 0),
                    (2151613002, 0), (2148653002, 0), (2027643002, 0),
                    (2085023003, 0), (2223093002, 0), (2177983004, 0),
                    (2140383005, 0), (2211423003, 0), (2256073002, 0),
                    (1999153002, 0), (2048483002, 0), (2151763003, 0),
                    (2148793002, 0)
                ])
            }

        actual = self.files.stat_reviews(year=2016)

        self.assertCountEqual(list(expected.keys()), list(actual.keys()))
        self.assertEqual(expected['reviews'], actual['reviews'])
        self.assertEqual(expected['open'], actual['open'])
        self.assertEqual(expected['messages'], actual['messages'])
        self.assertEqual(expected['patchsets'], actual['patchsets'])
        self.assertEqual(expected['comments'], actual['comments'])

    def test_transform_review(self):
        expected = [
                'cc/test/layer_tree_test.h',
                'cc/test/layer_tree_test.cc',
                'cc/layers/surface_layer_unittest.cc',
                'cc/trees/layer_tree_host_unittest.cc',
                'cc/trees/layer_tree_host_unittest_copyrequest.cc',
                'cc/trees/layer_tree_host_unittest_context.cc'
            ]

        actual = self.files.transform_review(
                self.files.get_review(id=2140383005)
            )

        self.assertCountEqual(expected, actual['reviewed_files'])
        self.assertCountEqual(expected, actual['committed_files'])

    def test_transform_review_keys_added(self):
        review = self.files.get_review(id=1999153002)
        expected = list(review.keys()) + ['reviewed_files', 'committed_files']

        actual = list(self.files.transform_review(review).keys())

        self.assertCountEqual(expected, actual)
