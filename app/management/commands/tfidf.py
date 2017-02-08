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
from app.queryStrings import *

ALL_RIDS = {
            'all':query_rIDs_all(), '2008':query_rIDs_by_year(2008),
            '2009':query_rIDs_by_year(2009), '2010':query_rIDs_by_year(2010),
            '2011':query_rIDs_by_year(2011), '2012':query_rIDs_by_year(2012),
            '2013':query_rIDs_by_year(2013), '2014':query_rIDs_by_year(2014),
            '2015':query_rIDs_by_year(2015), '2016':query_rIDs_by_year(2016),
            'fixed':query_rIDs_fixed(), 'missed':query_rIDs_missed(),
            'fixmis':[]
    }
ALL_RIDS['fixmis'] = ALL_RIDS['fixed'] + ALL_RIDS['missed']

def _getTermFrequencyDict(reviewID, useLemma=False):
    """
    Return a dictionary of key-value pairs where the key is either each unique
    token contained in all messages associated with the given reviewID or each
    unique lemma contained in all messages associated with the given reviewID.

    The value associated with each key in the dictionary is the Term Frequency
    of the key. Term Frequency (TF):

    TF = (# of occurrences of token in reviewID)/(# of total tokens in reviewID)
    """
    if useLemma:
        tf_dict = query_TF_dict(reviewID, lemma="lemma")
    else:
        tf_dict = query_TF_dict(reviewID, lemma="token")

#    print(tf_dict)
    return tf_dict

def _getTermFrequency(reviewID, term, useLemma):
    """
    Given a reviewID and a term, return the TF value of the term for the
    given reviewID. This is essentially a wrapper looking up values
    returned by getTermFrequencyDict() that handles the case where the given
    term does not appear in the reviewID (TF = 0)
    """
    tf_dict = _getTermFrequencyDict(reviewID, useLemma)
#    print(tf_dict)
    if term in tf_dict.keys():
        return tf_dict[term]
    else:
        return 0

def _getInverseDocumentFrequency(term, useLemma=False, population=['all']):
    """
    Given a term, return the Inverse Term Frequency of the term in the
    population. In unspecified, the population is the entire corpus. If
    specified, the population must equal:

    ['all']        : the entire corpus of reviews
    ['fixed']      : all reviews that fixed a vulnerability
    ['missed']     : all reviews that missed a vulnerability
    ['fixmis']     : the combination of 'fixed' and 'mixed'
    ['2008', etc.] : a list of valid review years within the corpus

    Inverse Document Frequency (IDF):
    IDF = log((# of total documents in the population) /
              (# of documents in the population that contain at least one
               occurrence of the given term)
             )
    """
    lemma = "lemma" if useLemma else "token"
    ids = []
#    print(population)
#    print(type(population))
    print(ALL_RIDS.keys())
    print(any(p not in ALL_RIDS.keys() for p in population))
    if len(population) == 0:
        raise ValueError("Population for IDF calculations cannot be empty!")
    elif any(p not in ALL_RIDS.keys() for p in population):
        raise ValueError(
                         "Specified population for IDF calculations is not "
                         "valid: " + str(population)
            )
    else:
        for key in population:
            ids += ALL_RIDS[key]

    print("LEN IDS: " + str(len(ids)))
    df = query_DF_dict(lemma, ids)
    idf = log10(len(ids) / df[term])

#    print("IDF: " + str(idf))
    return idf


def _getTFIDF(reviewID, term, useLemma=False, population=['all']):
    """
    Return the whole TF-IDF score for the given term in the given reviewID for
    the given population.
    """
    tf = _getTermFrequency(reviewID, term, useLemma)
    print("TF: " + str(tf))
    idf = _getInverseDocumentFrequency(term, useLemma, population)
    print("IDF: " + str(idf))
    tf_idf = float(tf) * float(idf)
#    print(tf_idf)

#    tf_idf = float(_getTermFrequency(reviewID, term, useLemma) *
#            _getInverseDocumentFrequency(term, useLemma, population))
    info("TF-IDF for term \'%s\' in review %s is %3.3f." %
        (term,reviewID,tf_idf))
    return tf_idf

def _tfidfForManyReviews(term, useLemma=False, population=['all']):
    for rID in population:
        tf_idf = _getTFIDF(rID, term, useLemma, population)


class Command(BaseCommand):
    """ Sets up the command line arguments. """
    help = 'Calculate and display the tf-idf score for a single code review ' \
           ' or all code reviews created in a specified year.'

    def add_arguments(self, parser):
        """
        -id     : a reviewID
        --lemma : if included, calculate TF-IDF for the lemma of the given term
        --pop   : if included, calculate TF-IDF against the given population,
                  else, calculate against the entire corpus of reviews
        term    : a single token to calculate TF-IDF for
        """
        parser.add_argument(
                '-id', type=int, default=None, help='Code review identifier '
                'of a code review to calculate tf-idf.')
        parser.add_argument(
                '--lemma', default=False, action='store_true', help='If '
                'included, the lemma of the specified term will be used.')
        parser.add_argument(
                '--pop', default=['all'], nargs='*', type=str,  help='If '
                'included, set the population for IDF to the given arguments.')
        parser.add_argument(
                'term', type=str, default=None, help='The term to calculate '
                'tf-idf for.')

    def handle(self, *args, **options):
        id = options.get('id', None)
        useLemma = options.get('lemma', False)
        population = options.get('pop', ['all'])
        term = options.get('term', None)
        begin = dt.now()

        if term is None:
            raise CommandError('term must be specified.')

        try:
            word = ''
            outputText = ''
            if useLemma:
                outputText = 'lemma'
                word = Lemmatizer([term]).execute()
                # This seems redundant, but appending '[0]' to the end of the
                # line above actually causes a 'not supscriptable' error.
                word = word[0]
                info("Using lemma \'%s\' of term \'%s\'." % (word,term))
            else:
                outputText = 'token'
                word = term

            if id is not None:
                info("Calculating TF-IDF of %s \'%s\' for review %s in the "
                    "population: %s" %
                    (outputText,word,str(id),str(population)))
                begin = dt.now()
                print(_getTFIDF(id, word, useLemma, population))
            elif population != [] and population != ['']:
                info("Calculating TF-IDF of %s \'%s\' for all reviews in the "
                     "population: %s" % (outputText,word,str(population)))
                begin = dt.now()
                print(_tfidfForManyReviews(word, useLemma, population))
            else:
                raise CommandError('The specified population is invalid.')

        except KeyboardInterrupt:
            warning('Attempting to abort.')
        finally:
            info('Time: {:.2f} mins'.format(get_elapsed(begin, dt.now())))
