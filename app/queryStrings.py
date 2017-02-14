"""
@AUTHOR: meyersbs
"""

import random

from django.contrib.postgres import fields
from django.db.models import Count, Sum, Q
from itertools import chain

from app.models import *

ALL_IDS = []
FIXED_IDS = []
MISSED_IDS = []
NEUTRAL_IDS = []
NEUTRAL_MISSED = []
NEUTRAL_FIXED = []
FIXED_MISSED = []

#### TF-IDF ####################################################################
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

#### Messages ##################################################################
def query_mIDs(population):
    """ Passthrough function for determining which queries to run. """

    pop_dict = {'all': query_mIDs_all, 'fixed': query_mIDs_fixed,
                'missed': query_mIDs_missed, 'fm': query_mIDs_fm,
                'random': query_mIDs_random, 'nf': query_mIDs_nf,
                'nm': query_mIDs_nm, 'neutral': query_mIDs_neutral}

    if population in pop_dict.keys():
        return pop_dict[population]()
    else:
        return query_mIDs_year(population)

def query_mIDs_all():
    """ Return a list of all message IDs. """
    queryResults = Message.objects.all().values_list('id', flat=True)

    return queryResults

def query_mIDs_random():
    """ Returns a list of all review IDs in the corpus. """
    queryResults = Message.objects.all().values_list('id', flat=True)
    r = random.randint(0, 50) * random.randint(1, 5)

    return queryResults[r:r+500]

def query_mIDs_fixed():
    """ Returns a list of message IDs that fixed a vulnerability. """
    review_ids = query_rIDs_fixed()
    queryResults = Message.objects.filter(review_id__in=review_ids) \
        .values_list('id', flat=True)

    return queryResults

def query_mIDs_missed():
    """ Returns a list of message IDs that missed a vulnerability. """
    review_ids = query_rIDs_missed()

    queryResults = Message.objects.filter(review_id__in=review_ids) \
        .values_list('id', flat=True)

    return queryResults

def query_mIDs_neutral():
    """
    Returns a list of message IDs that have not fixed or missed a vulnerability.
    """
    missed = query_mIDs_missed()
    fixed = query_mIDs_fixed()

    queryResults = Message.objects \
        .exclude(Q(id__in=missed) | Q(id__in=fixed)) \
        .values_list('id', flat=True)

    return queryResults

def query_mIDs_fm():
    """
    Returns a list of message IDs that have fixed or missed a vulnerability.
    """
    missed = query_mIDs_missed()
    fixed = query_mIDs_fixed()

    queryResults = Message.objects \
        .filter(Q(id__in=missed) | Q(id__in=fixed)) \
        .values_list('id', flat=True)

    return queryResults

def query_mIDs_nf():
    """
    Returns a list of message IDs that have fixed a vulnerability or have not
    missed a vulnerability.
    """
    missed = query_mIDs_missed()

    queryResults = Message.objects.exclude(id__in=missed) \
        .values_list('id', flat=True)

    return queryResults

def query_mIDs_year(year):
    """ Returns a list of message IDs from the specified year. """
    years = [str(i) for i in range(2008, 2017)]
    if year not in years:
        raise ValueError('Received unknown year for query_messages_year().')
    else:
        queryResults = Message.objects.filter(posted__year=int(year)) \
            .values_list('id', flat=True)

    return queryResults

def query_mIDs_nm():
    """
    Returns a list of message IDs that have missed a vulnerability or have not
    fixed a vulnerability.
    """
    fixed = query_mIDs_fixed()

    queryResults = Message.objects.exclude(id__in=fixed) \
        .values_list('id', flat=True)

    return queryResults

def query_mID_text(message_id):
    """ Return the text field of the given message. """
    queryResults = Message.objects.filter(id__exact=message_id) \
        .values_list('text', flat=True)

    return queryResults[0]

#### Reviews ###################################################################
def query_rIDs(population):
    """ Passthrough function for determining which queries to run. """
    global ALL_IDS, FIXED_IDS, MISSED_IDS, NEUTRAL_IDS
    pop_dict = {'all': query_rIDs_all, 'fixed': query_rIDs_fixed,
                'missed': query_rIDs_missed, 'fm': query_rIDs_fm,
                'random': query_rIDs_random, 'nf': query_rIDs_nf,
                'nm': query_rIDs_nm, 'neutral': query_rIDs_neutral}

    ALL_IDS = query_rIDs_all()
    FIXED_IDS = query_rIDs_fixed()
    MISSED_IDS = query_rIDs_missed()
    NEUTRAL_IDS = list(set(ALL_IDS) - set(FIXED_IDS))
    NEUTRAL_IDS = list(set(NEUTRAL_IDS) - set(MISSED_IDS))

    if population in pop_dict.keys():
        return pop_dict[population]()
    else:
        return query_rIDs_year(population)

def query_rIDs_all():
    """ Returns a list of all review IDs in the corpus. """
    global ALL_IDS
    queryResults = Review.objects.all().values_list('id', flat=True)

    ALL_IDS = list(queryResults)

    return queryResults

def query_rIDs_random(review_ids, rand):
    """ Returns a list of all review IDs in the corpus. """
    queryResults = list(Review.objects.filter(id__in=review_ids) \
        .order_by('?').values_list('id', flat=True)[0:rand])

    return queryResults

def query_rIDs_year(year):
    """ Returns a list of review IDs from the specified year. """
    years = [str(i) for i in range(2008, 2017)]
    if year not in years:
        raise ValueError('Received unknown year for query_rIDs_year().')
    else:
        queryResults = Review.objects.filter(created__year=int(year)) \
            .values_list('id', flat=True)

    return queryResults

def query_rIDs_fixed():
    """ Returns a list of review IDs that fixed a vulnerability. """
    global FIXED_IDS
    if len(FIXED_IDS) > 0:
        return FIXED_IDS
    queryResults = VulnerabilityBug.objects.distinct('bug__review__id') \
        .exclude(bug__review__id__exact=None) \
        .values_list('bug__review__id', flat=True)

    FIXED_IDS = list(queryResults)

    return queryResults

def query_rIDs_missed():
    """ Returns a list of review IDs that missed a vulnerability. """
    global MISSED_IDS
    if len(MISSED_IDS) > 0:
        return MISSED_IDS
    queryResults = Review.objects.filter(missed_vulnerability=True) \
        .values_list('id', flat=True)

    MISSED_IDS = list(queryResults)

    return queryResults

def query_rIDs_neutral():
    """
    Returns a list of review IDs that have not fixed or missed a vulnerability.
    """
    global NEUTRAL_IDS
    if len(NEUTRAL_IDS) > 0:
        return NEUTRAL_IDS

    missed = query_rIDs_missed()
    nm = query_rIDs_nm(ret='raw')

    queryResults = nm.exclude(id__in=missed) \
        .values_list('id', flat=True)

    NEUTRAL_IDS = list(queryResults)

    return queryResults

def query_rIDs_fm():
    """
    Returns a list of review IDs that have fixed or missed a vulnerability.
    """
    global FIXED_MISSED
    if len(FIXED_MISSED) > 0:
        return FIXED_MISSED

    fixed = query_rIDs_fixed()
    missed = query_rIDs_missed()

    FIXED_MISSED = list(set(fixed) | set(missed))
    return FIXED_MISSED

def query_rIDs_nf():
    """
    Returns a list of review IDs that have fixed a vulnerability or have not
    missed a vulnerability.
    """
    global ALL_IDS, NEUTRAL_FIXED
    if len(NEUTRAL_FIXED) > 0:
        return NEUTRAL_FIXED

    missed = query_rIDs_missed()

    NEUTRAL_FIXED = list(set(ALL_IDS) - set(missed))
    return NEUTRAL_FIXED

def query_rIDs_nm():
    """
    Returns a list of review IDs that have missed a vulnerability or have not
    fixed a vulnerability.
    """
    global ALL_IDS, NEUTRAL_MISSED
    if len(NEUTRAL_MISSED) > 0:
        return NEUTRAL_MISSED

    fixed = query_rIDs_fixed()

    NEUTRAL_MISSED = list(set(ALL_IDS) - set(fixed))
    return NEUTRAL_MISSED

def query_tokens(review_ids, use_lemma=False):
    if use_lemma:
        queryResults = ReviewLemmaView.objects.distinct('lemma') \
            .filter(review_id__in=review_ids) \
            .values_list('lemma', flat=True)
    else:
        queryResults = ReviewTokenView.objects.distinct('token') \
            .filter(review_id__in=review_ids) \
            .values_list('token', flat=True)

    return queryResults

def query_tokens_all(use_lemma=False):
    if use_lemma:
        queryResults = ReviewLemmaView.objects.distinct('lemma') \
            .values_list('lemma', flat=True)
    else:
        queryResults = ReviewTokenView.objects.distinct('token') \
            .values_list('token', flat=True)

    return queryResults

def query_top_x_tokens(review_ids, x, use_lemma=False):
    message_ids = Message.objects.distinct('id') \
        .filter(review_id__in=review_ids) \
        .values_list('id', flat=True)

    if use_lemma:
        queryResults = Token.objects \
            .filter(message__review__id__in=review_ids) \
            .filter(lemma__iregex=r"\w+") \
            .values('lemma') \
            .annotate(freq=Sum('frequency')) \
            .order_by('-freq') \
            .values_list('lemma', flat=True)
    else:
        queryResults = Token.objects \
            .filter(message__review__id__in=review_ids) \
            .filter(token__iregex=r"\w+") \
            .values('token') \
            .annotate(freq=Sum('frequency')) \
            .order_by('-freq') \
            .values_list('token', flat=True)

    return queryResults[0:x]
