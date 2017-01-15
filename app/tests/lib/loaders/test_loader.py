from django import test
from django.conf import settings

from app.lib.loaders import loader


class LoaderTestCase(test.TestCase):
    def setUp(self):
        self.loader = loader.Loader(settings)

    def test_load(self):
        self.assertRaises(NotImplementedError, self.loader.load)
