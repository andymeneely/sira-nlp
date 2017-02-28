import os
import signal
import subprocess

#from unittest import TestCase
from django import test
from django.conf import settings

from app.models import *
from app.lib import helpers, loaders, taggers
from app.management.commands.complexity import *
from app.queryStrings import *
from django.db import connection, connections

from django.core.management import call_command
from django.db import transaction
from django.test import TransactionTestCase, override_settings

class ComplexityTestCase(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        loader = loaders.ReviewLoader(settings, 1)
        _ = loader.load()
        rIDs = query_rIDs_all()
#        connections.close_all()
        loader = loaders.MessageLoader(settings, 1, list(rIDs))
        _ = loader.load()
#        connections.close_all()
#        tagger = taggers.ComplexityTagger(settings, 1, rIDs)
#        _ = tagger.tag()
#        connections.close_all()
#        call_command('loaddb')
#        cls.db = 
#        pass

    def setUp(self):
        print(query_rIDs_all())
        print(query_mIDs_all())

    def test_run_all_analyses(self):
        data = [392]
        expected = []
        actual = run_all_analyses(data, False)
        print(actual)
        pass
