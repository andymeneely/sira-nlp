"""
@AUTHOR: meyersbs
"""

import csv
import multiprocessing
import json

from datetime import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection, connections
from django.db.models import Q

from app.lib import loaders, taggers
from app.lib.external import *
from app.lib.helpers import *
from app.lib.logger import *
from app.models import *

from app.lib.nlp.sentenizer import NLTKSentenizer
from app.lib.nlp.analyzers import SentenceParseAnalyzer

import app.queryStrings as qs

#### FUNCTIONS FOR PARSING THE STANFORD POLITENESS TRAINING DATA ###############
def find_last_occurrence(depparse):
    """
    Given a list of dependencies, return the index of the last 'ROOT(.*)'
    dependency. This is necessary because, for some strange reason, the
    'depparse' list in get_depparse() is not being reset in the loop. The
    most probable cause has something to do with how the SentenceParseAnalyzer
    object returns data.
    """
    start = -1
    for i, item in enumerate(reversed(depparse)):
        if item[0:4] == 'ROOT':
            start = len(depparse) - i - 1
            break

    return start

def get_depparse(text):
    """
    Given the text from one of the annotated Stanford Politeness Corpus files,
    return a dictionary of the form:
        {'text': str, 'sentences': list, 'parses': list, 'score': float}
    This is the expected format of the politeness classifier training script in:
        app/lib/external/politeness/scripts/train_model.py
    """
    sentences = NLTKSentenizer(text).execute()
    results = {'text': "", 'sentences': [], 'parses': [], 'score': 0.0}
    results['text'] = text
    for sent in sentences:
        results['sentences'].append(sent)
        response = SentenceParseAnalyzer(sent).analyze()
        depparse = []
        for dep in response['deps']:
            temp = str(dep['dep'] + "(" +
                       dep['governorGloss'].lower() + "-"
                       + str(dep['governor']) + ", " +
                       dep['dependentGloss'] + "-" +
                       str(dep['dependent']) + ")")
            depparse.append(temp)
        start = find_last_occurrence(depparse)
        results['parses'].append(depparse[start:])
    return results


################################################################################

class Command(BaseCommand):
    """
    Sets up command line arguments.
    """
    help = 'Load the database with sentence text and parses.'

    def add_arguments(self, parser): # pragma: no cover
        """

        """
        parser.add_argument(
                '--processes', dest='processes', type=int,
                default=settings.CPU_COUNT, help='Number of processes to spawn.'
                ' Default is {}'.format(settings.CPU_COUNT)
            )
        parser.add_argument(
                '--condition', type=str, default='all', dest='condition',
                choices=['all', 'empty', 'failed'], help="The sentences to "
                "repopulate parses for. Defualt is 'all'."
            )
        parser.add_argument(
                '--year', type=int, dest='year', default=0, choices=[2008,
                2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 0],
                help='If specified, only sentences in the given year will be'
                ' parsed.'
            )

    def handle(self, *args, **options): # pragma: no cover
        """

        """
        processes = options['processes']
        condition = options['condition']
        year = options['year']
        begin = dt.now()
        try:
            if year == 0:
                sents = qs.query_all('sentence', ids=False)
            else:
                sents = qs.query_by_year(year, 'sentence', ids=False)

            if condition == 'all':
                sents = sents.exclude(text='').iterator()
            elif condition == 'empty' or condition == 'failed':
                sents = sents.filter(parses={}).exclude(text='').iterator()

            connections.close_all()
            tagger = taggers.SentenceParseTagger(settings, processes, sents)
            tagger.tag()

        except KeyboardInterrupt:
            warning('Attempting to abort.')
        finally:
            info('Time: {:.2f} mins'.format(get_elapsed(begin, dt.now())))
