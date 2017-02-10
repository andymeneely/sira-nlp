"""
@AUTHOR: meyersbs
"""

import random

from django.contrib.postgres import fields
from django.db.models import Count, Sum
from itertools import chain

from app.models import *

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

    pop_dict = {'all': query_rIDs_all, 'fixed': query_rIDs_fixed,
                'missed': query_rIDs_missed, 'fixmiss': query_rIDs_fixmiss,
                'random': query_rIDs_random}

    if population in pop_dict.keys():
        return pop_dict[population]()
    else:
        return query_rIDs_year(population)

def query_rIDs_all():
    """ Returns a list of all review IDs in the corpus. """
    queryResults = Review.objects.all().values_list('id', flat=True)

    return queryResults

def query_rIDs_random():
    """ Returns a list of all review IDs in the corpus. """
    queryResults = Review.objects.all().values_list('id', flat=True)
    r = random.randint(0, 50) * random.randint(1, 5)

    return queryResults[r:r+500]

def query_rIDs_year(year):
    """ Returns a list of review IDs from the specified year. """
    years = [str(i) for i in range(2008, 2017)]
    if year not in years:
        raise CommandError('Received unknown population for TF-IDF.')
    else:
        queryResults = Review.objects.filter(created__year=int(year)) \
            .values_list('id', flat=True)

    return queryResults

def query_rIDs_fixed():
    """ Returns a list of review IDs that fixed a vulnerability. """
    queryResults = VulnerabilityBug.objects.distinct('bug__review__id') \
        .values_list('bug__review__id', flat=True)

    return queryResults

def query_rIDs_missed():
    """ Returns a list of review IDs that missed a vulnerability. """
    queryResults = Review.objects.filter(missed_vulnerability=True) \
        .values_list('id', flat=True)

    return queryResults

def query_rIDs_fixmiss():
    """
    Returns a list of review IDs that have fixed or missed a vulnerability.
    """
    fixed = list(query_rIDs_fixed())
    missed = list(query_rIDs_missed())

    queryResults = fixed + missed
    print(len(queryResults))
    print(type(queryResults))

    return queryResults

def query_tokens(review_ids):
    queryResults = ReviewTokenView.objects.distinct('token') \
        .filter(review_id__in=review_ids) \
        .values_list('token', flat=True)

    return queryResults

def query_tokens_all():
    queryResults = ReviewTokenView.objects.distinct('token') \
        .values_list('token', flat=True)

    return queryResults
