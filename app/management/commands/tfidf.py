"""
@AUTHOR: meyersbs
"""

import csv
import glob
import operator
import os

from math import log10
from datetime import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from app.lib.files import *
from app.lib.helpers import *
from app.lib.logger import *
from app.lib.nlp.lemmatizer import Lemmatizer
from app.lib.rietveld import *
from app.queryStrings import *

ALL_REVIEW_IDS = {0:[], 2008:[], 2009:[], 2010:[], 2011:[], 2012:[], 2013:[],
                 2014:[], 2015:[], 2016:[]}


def calculateForAllReviews(word, useLemma, t=None):
    """

    """
    scores = []
    for i in range(2008, 2017):
        info("=== Year: %i ===" % i)
        score, _ = calculateForYear(i, word, useLemma, t=t)
        scores += score

    return scores, dt.now()

def calculateForOneReview(reviewID, word, year, useLemma, totals=None):
    """

    """
    if useLemma:
        tf = queryTermFrequency(word, reviewID, lemma="base")
        df = queryDocumentFrequency(word, year, lemma="base")
    else:
        tf = queryTermFrequency(word, reviewID, lemma="text")
        df = queryDocumentFrequency(word, year, lemma="text")

    total = 0
    if year is None:
        total = totals[0]
    else:
        total = totals[year]

    try:
        # +1 to pad result against df==0
        idf = log10(float(total)/float(df + 1))
    except ValueError as e:
        warning("Value Error: " + str(e))

    tf_idf = float(tf) * float(idf)

    return tf_idf, dt.now()

def calculateForYear(year, word, useLemma, t=None):
    """
    Calculates the TF-IDF for the given term for all reviews from the given
    year. Returns a list of tf_idf scores and the current system time.
    """
    global ALL_REVIEW_IDS
    scores = []
    skipped = 0
    for r in ALL_REVIEW_IDS[year]:
        tf_idf, _ = calculateForOneReview(r, word, year, useLemma, totals=t)
        scores.append(tf_idf)
        if tf_idf == 0:
            skipped += 1
        else:
            if useLemma:
                info("TF-IDF for lemma \'%s\' in review %i is %3.3f." % \
                    (word,r,tf_idf))
            else:
                info("TF-IDF for term \'%s\' in review %i is %3.3f." % \
                    (word,r,tf_idf))

    if skipped == len(ALL_REVIEW_IDS[year]):
        info("There are no reviews from %i that contain \'%s\'." % \
            (year,word))
    elif skipped > 0:
        info("Skipped %i reviews where TF-IDF was 0" % skipped)
    else:
        pass

    return scores, dt.now()


class Command(BaseCommand):
    """
    Sets up the command line arguments.
    """
    help = 'Calculate and display the tf-idf score for a single code review ' \
           ' or all code reviews created in a specified year.'

    def add_arguments(self, parser):
        """

        """
        parser.add_argument(
                '-id', type=int, default=None, help='Code review identifier '
                'of a code review to calculate tf-idf.')
        parser.add_argument(
                '-year', type=int, default=None, help='tf-idf of all code '
                'reviews created in the specified year will be aggregated. '
                'Argument is ignored when id is specified.')
        parser.add_argument(
                '--lemma', default=False, action='store_true', help='If '
                'included, the lemma of the specified term will be used.')
        parser.add_argument(
                '--all', default=False, action='store_true', help='If '
                'included, ignore -id and -year, and calculate TF-IDF '
                'for the specified term for every document.')
        parser.add_argument(
                'term', type=str, default=None, help='The term to calculate '
                'tf-idf for.')

    def handle(self, *args, **options):
        """

        """
        global ALL_REVIEW_IDS
        id = options.get('id', None)
        year = options.get('year', None)
        term = options.get('term', None)
        useLemma = options.get('lemma', False)
        all = options.get('all', False)
        word = ""
        endTime = dt.now()
        outputText = 'term'

        try:
            if term is None:
                begin = dt.now()
                raise CommandError('term must be specified')
            elif id is None and year is None and all is False:
                begin = dt.now()
                raise CommandError('id, year, or all must be provided')
            else:
                if useLemma:
                    outputText = 'lemma'
                    word = Lemmatizer([term]).execute()
                    word = word[0]
                    info("Using lemma \'%s\' of term \'%s\'." % (word,term))
                else:
                    outputText = 'term'
                    word = term

                TOTALS = {}
                ALL_REVIEW_IDS[0], TOTALS[0] = queryAllReviews()
                for i in range(2008, 2017):
                    ALL_REVIEW_IDS[i], TOTALS[i] = queryReviewsByYear(i)
                print(TOTALS)

                begin = dt.now()
                if all:
                    info("Calculating TF-IDF of %s \'%s\' for all reviews." %
                        (outputText,word))
                    scores, endTime = calculateForAllReviews(word, useLemma, t=TOTALS)
                elif id is not None:
                    info("Calculating TF-IDF of %s \'%s\' for review %i." %
                        (outputText,word,id))
                    tf_idf, endTime = calculateForOneReview(id, word, None, useLemma, totals=TOTALS)
                    info("TF-IDF for %s \'%s\' in review %i is %3.3f." %
                        (outputText,word,id,tf_idf))
                elif year is not None:
                    info("Calculating TF-IDF of %s \'%s\' for all reviews "
                        "from %i." % (outputText,word,year))
                    scores, endTime = calculateForYear(year, word, useLemma, t=TOTALS)
                else:
                    raise CommandError('id, year, or all must be provided')
        except KeyboardInterrupt:
            warning('Attempting to abort.')
        finally:
            info('Time: {:.2f} mins'.format(get_elapsed(begin, endTime)))

#        begin = dt.now()
#        try:
#            if id is not None:
#                if lemma:
#                    tf = queryTermFrequency(word, id, lemma="base")
#                    df = queryDocumentFrequency(word, lemma="base")
#                else:
#                    tf = queryTermFrequency(word, id)
#                    df = queryDocumentFrequency(word)
#
#                total = queryTotalDocuments()
#
#                try:
#                    # +1 to pad result against df==0
#                    idf = log10(float(total)/float(df + 1))
#                except ValueError as e:
#                    warning("Value Error: " + str(e))
#
#                tf_idf = float(tf) * float(idf)
#
#                info("TF-IDF for term \'%s\' in review %i is %3.3f." % \
#                    (word,id,tf_idf))
#            else:
#                revIDs = queryReviewsByYear(year)
#                if lemma:
#                    df = queryDocumentFrequency(word, year, lemma="base")
#                else:
#                    df = queryDocumentFrequency(word, year)
#
#                total = queryTotalDocuments(year)
#
#                try:
#                    # +1 to pad result against df==0
#                    idf = log10(float(total)/float(df + 1))
#                except ValueError as e:
#                    warning("Value Error: " + str(e))
#
#                info('TF-IDF for reviews from %i:' % year)
#                skipped = 0
#                for r in revIDs:
#                    if lemma:
#                        tf = queryTermFrequency(word, r, lemma="base")
#                    else:
#                        tf = queryTermFrequency(word, r)
#
#                    tf_idf = float(tf) * float(idf)
#
#                    if tf_idf == 0:
#                        skipped += 1
#                    else:
#                        info("TF-IDF for term \'%s\' in review %i is %3.3f." % \
#                            (word,r,tf_idf))
#
#                if skipped > 0:
#                    info("Skipped %i reviews where TF-IDF was 0" % skipped)
#                else:
#                    info("There are no reviews from %i that contain \'%s\'." % \
#                        (year,word))
#
#        except KeyboardInterrupt:
#            warning('Attempting to abort.')
#        finally:
#            info('Time: {:.2f} mins'.format(get_elapsed(begin, endTime)))
