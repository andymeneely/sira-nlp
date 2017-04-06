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
from app.queryStrings import *

from app.lib.nlp.sentenizer import NLTKSentenizer
from app.lib.nlp.analyzers import SentenceParseAnalyzer

from bulk_update.helper import bulk_update

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

def populate_dependencies(out_to_file=True): # pragma: no cover
    """
    For the annotated StackExchange and Wikipedia data files, generate the
    dependency parses and format the data in the expected format for the
    politeness classifier trainer. Dump the output as a json string to the disk.

    TAGGED_STACK_EXCHANGE and TAGGED_WIKIPEDIA are CSV files with columns 0-13:
        [   0] Community        - where the entry came from
        [   1] Id 	        - unique identifier
        [   2] Request 	        - the actual text for the entry
        [3- 7] Score1-5         - the raw politeness scores (0-25) assigned
        [8-12] TurkId1-5        - identifier for machanical turk users
        [  13] Normalized Score - the normalized, average politeness score

    For our purposes, we only care about columns 2 and 13.
    """
    stack_sents = []
    cnt = 0
    with open(TAGGED_STACK_EXCHANGE, 'r', newline='') as csvfile:
        stack_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in stack_reader:
            temp = get_depparse(row[2]) # column 2
            temp['score'] = row[13] # column 13
            stack_sents.append(temp)
            print(cnt)
            cnt+=1

    if out_to_file:
        with open(PARSED_STACK_EXCHANGE, 'w') as f:
            f.write(json.dumps(stack_sents[1:]))
    else:
        return stack_sents[1:]

    wiki_sents = []
    cnt = 0
    with open(TAGGED_WIKIPEDIA, 'r', newline='') as csvfile:
        wiki_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in wiki_reader:
            temp = get_depparse(row[2]) # column 2
            temp['score'] = row[13] # column 13
            wiki_sents.append(temp)
            print(cnt)
            cnt+=1

    if out_to_file:
        with open(PARSED_WIKIPEDIA, 'w') as f:
            f.write(json.dumps(wiki_sents[1:]))
    else:
        return wiki_sents[1:]

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
                '--stanford', default=False, action='store_true', help='If '
                'specified, ignore --pop and append the dependency parses to '
                'the end of each of the stanford politeness dataset sentences.'
            )

    def handle(self, *args, **options): # pragma: no cover
        """

        """
        processes = options['processes']
        condition = options['condition']
        stanford = options['stanford']
        begin = dt.now()
        try:
            if stanford:
                populate_dependencies()
            else:
                sents = []
                if condition == 'all':
                    sents = Sentence.objects.exclude(text='').iterator()
                elif condition == 'empty':
                    sents = Sentence.objects.filter(parses={}).exclude(text='').iterator()
                elif condition == 'failed':
                    sents = Sentence.objects.exclude(text='').filter(
                                parses={'depparse': 'X', 'treeparse': 'X'}).iterator()

                connections.close_all()
                tagger = taggers.SentenceParseTagger(settings, processes, sents)
                tagger.tag()

        except KeyboardInterrupt:
            warning('Attempting to abort.')
        finally:
            info('Time: {:.2f} mins'.format(get_elapsed(begin, dt.now())))
