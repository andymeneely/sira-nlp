"""
@AUTHOR: meyersbs
"""

import csv
import glob
import operator
import os

from math import log10
from datetime import datetime as dt
from datetime import time

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from app.lib.files import *
from app.lib.helpers import *
from app.lib.logger import *
from app.lib.nlp.lemmatizer import NLTKLemmatizer
from app.lib.nlp.tokenizer import *
from app.lib.rietveld import *
from app.queryStrings import *

START_NLTK = dt.now()
END_NLTK = dt.now()

def lemmatizeAllMessages():

    elapsed_nltk = 0
    start = dt.now()
    for i in range(2008, 2017):
        elapsed_nltk = lemmatizeMessagesByYear(i)

    end = dt.now()
    info('NLTK Total Processing Time: {:n} minutes.'.format(elapsed_nltk))

    return end

def lemmatizeOneMessage(message):
    global END_NLTK

    print(message.id)
    tokens = NLTKTokenizer(message.text).execute()
    print(tokens)
    startNLTK = dt.now()
    print(NLTKLemmatizer(tokens).execute())
    END_NLTK = dt.now()

    return get_elapsed(startNLTK, END_NLTK)

def lemmatizeMessagesByYear(year):
    global START_NLTK, END_NLTK

    messages = queryMessagesByYear(year)
    info('=== {:n} ==='.format(year))

    elapsed_nltk = 0
    START_NLTK = dt.now()
    for m in messages:
        elapsed_nltk = lemmatizeOneMessage(m)
    info('NLTK lemmatized all messages from {:n} in {:.2f} mins'.format(year, get_elapsed(START_NLTK, END_NLTK)))
    info('NLTK Processing Time: {:n} minutes'.format(elapsed_nltk))

    return elapsed_nltk, dt.now()

class Command(BaseCommand):
    """
    Sets up the command line arguments.
    """
    help = 'Run tests for Lemmatization of messages.'

    def add_arguments(self, parser):
        parser.add_argument(
                '-year', type=int, default=None, help='Lemmatize all messages ')
        parser.add_argument(
                '--all', default=False, action='store_true', help='If '
                'included, ignore -year, and lemmatize all messages in the '
                'database')

    def handle(self, *args, **options):
        global ALL_REVIEW_IDS
        year = options.get('year', None)
        all = options.get('all', False)
        endTime = dt.now()

        try:
            if all:
                begin = dt.now()
                endTime = lemmatizeAllMessages()
            elif year is not None:
                begin = dt.now()
                endTime = lemmatizeMessagesByYear(year)[1]
            else:
                begin = dt.now()
                endTime = dt.now()
                raise CommandError('-year or --all must be specified')
        except KeyboardInterrupt:
            warning('Attempting to abort.')
            endTime = dt.now()
        finally:
            info('Time: {:.2f} mins'.format(get_elapsed(begin, endTime)))
