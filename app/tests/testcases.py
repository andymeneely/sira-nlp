from django import test


class SpecialTestCase(test.TransactionTestCase):
    @classmethod
    def setUpClass(cls):
        cls.setUpTestData()
        super().setUpClass()
