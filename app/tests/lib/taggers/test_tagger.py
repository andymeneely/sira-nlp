from django import test
from django.conf import settings

from app.lib.taggers import tagger


class TaggerTestCase(test.TestCase):
    def setUp(self):
        self.tagger = tagger.Tagger(settings)

    def test_load(self):
        self.assertRaises(NotImplementedError, self.tagger.tag)
