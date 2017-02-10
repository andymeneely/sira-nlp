"""
@AUTHOR: meyersbs
"""

from unittest import TestCase
from app.queryStrings import *

class QueryStringsTestCase(TestCase):
    def setUp(self):
        pass

    def test_query_TF_dict(self):
        review_id = 1444413002
        use_lemma = False
        expected = {}
        actual = query_TF_dict(review_id, use_lemma)
        print(actual)
        pass

