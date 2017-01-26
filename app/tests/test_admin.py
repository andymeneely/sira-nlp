"""
@AUTHOR: meyersbs
"""

from unittest import TestCase

from app import admin


class AdminTestCase(TestCase):
    """
    This is an empty django file. It is not used in the codebase, but django
    requires it to exist. It gets counted as being 0% covered, so here's a
    dummy test case.
    """
    def setUp(self):
        pass

    def test_admin(self):
        self.assertEqual(True, True)
