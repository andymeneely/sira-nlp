"""
@AUTHOR: meyersbs
"""

from django.contrib.postgres import fields
from django.db.models import Count
from app.models import *

POP_DICT = {'all': _query_rIDs_all,
            'fixed': _query_rIDs_fixed,
            'missed': _query_rIDs_missed}

def query_TF_dict(review_id, use_lemma=False):
    """
    Returns the numerator of TF, the number of occurrences of the token in
    the review.
    """
    column = ''
    if use_lemma:
        column = 'lemma'
    else:
        column = 'token'

    queryResults = Token.objects.filter(message__review__id=review_id) \
        .values(column).annotate(tf=Sum('frequency'))

    return queryResults

def query_DF(review_ids, use_lemma=False):
    """
    Returns the denominator of DF, the number of documents in the population
    that contain the token at least once.
    """
    queryResults = None
    if use_lemma:
        queryResults = ReviewLemmaView.objects \
            .filter(review_id__in=review_ids).values('lemma') \
            .annotate(df=Count('lemma')).order_by('-df')
    else:
        queryResults = ReviewTokenView.objects \
            .filter(review_id__in=review_ids).values('token') \
            .annotate(df=Count('token')).order_by('-df')

    return queryResults

def query_rIDs(population):
    """ Passthrough function for determining which queries to run. """
    global POP_DICT
    if population in POP_DICT.keys():
        return POP_DICT[population]()
    elif population == 'fixmiss':
        return _query_rIDs_fixed() + query_rIDs_missed()
    else:
        return _query_rIDs_year(population)

def _query_rIDs_all():
    """ Returns a list of all review IDs in the corpus. """
    queryResults = Review.objects.all().values_list('id', flat=True)

    return queryResults

def _query_rIDs_year(year):
    """ Returns a list of review IDs from the specified year. """
    years = [str(i) for i in range(2008, 2017)]
    if year not in years:
        raise CommandError('Received unknown population for TF-IDF.')
    else:
        queryResults = Review.objects.filter(created__year=int(year)) \
            .values_list('id', flat=True)

    return queryResults

def _query_rIDs_fixed():
    """ Returns a list of review IDs that fixed a vulnerability. """
    queryResults = VulnerabilityBug.objects.distinct('bug__review__id') \
        .values_list('bug__review__id', flat=True)

    return queryResults

def _query_rIDs_missed():
    """ Returns a list of review IDs that missed a vulnerability. """
    queryResults = Review.objects.filter(missed_vulnerability=True) \
        .values_list('id', flat=True)

    return queryResults
