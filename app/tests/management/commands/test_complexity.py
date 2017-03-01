import os
import signal
import subprocess

from django import test
from django.conf import settings

from app.models import *
from app.lib import helpers, loaders, taggers
from app.management.commands.complexity import *
from app.queryStrings import *


class ComplexityTestCase(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def setUp(self):
        pass

'''
    def test_run_all_analyses(self):
        data = [392]
        expected = []
        actual = run_all_analyses(data, False)
        print(actual)
        pass
'''
