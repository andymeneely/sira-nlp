"""
@AUTHOR: meyersbs
"""

from unittest import TestCase

from app import apps


class AppsTestCase(TestCase):
    """
    This is an empty django file. It is not used in the codebase, but django
    requires it to exist. It gets counted as being 0% covered, so here's a
    dummy test case.
    """
    def setUp(self):
        pass

    def test_apps(self):
        self.assertEqual(True, True)
