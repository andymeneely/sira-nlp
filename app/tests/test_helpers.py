from django.test import TestCase

from app.lib.helpers import *


class HelpersTestCase(TestCase):
    def setUp(self):
        pass

    def test_truncate(self):
        # Arrange
        data = ['0123456789', 'foo', '']
        expected = ['012...', 'foo', '']

        # Act
        actual = [truncate(item, length=3) for item in data]

        # Assert
        self.assertEqual(expected, actual)

    def test_normalize(self):
        # Arrange
        data = {'data': '{base}/data', 'ids': '{base}/data/ids', 'base': '.'}
        expected = {
                'data': '/home/djinn/data', 'ids': '/home/djinn/data/ids',
                'base': '.'
            }

        # Act
        actual = normalize(data, using='/home/djinn')

        # Assert
        self.assertEqual(expected, actual)
