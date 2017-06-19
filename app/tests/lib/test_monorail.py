from unittest import TestCase

from django.conf import settings

from app.lib.monorail import *


class MonorailTestCase(TestCase):
    def setUp(self):
        self.monorail = Monorail(
                settings.MONORAIL_URL, settings.GOOGLESA_KEYFILE
            )

    def test_get_bug(self):
        data = 5608

        actual = self.monorail.get_bug(data)

        self.assertEqual(5608, actual['id'])
        self.assertEqual(7, len(actual['comments']))

    def test_get_bugs(self):
        data = [5608, 1678]

        actual = self.monorail.get_bugs(data, processes=2)

        (bugs, errors) = actual
        self.assertEqual(2, len(bugs))
        self.assertCountEqual([5608, 1678], [bug['id'] for bug in bugs])
        self.assertCountEqual([7, 10], [len(bug['comments']) for bug in bugs])
        self.assertEquals(list(), errors)
