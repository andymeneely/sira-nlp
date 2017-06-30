"""
@AUTHOR: meyersbs
"""

import math
import random

from django.contrib.postgres import fields
from django.db import connection
from django.db.models import Count, Sum, Q
from django.db.models.functions import Cast
from itertools import chain

from app.models import *
from app.lib.logger import *

OBJECTS = {
        'review': {'all': [], 'fixed': [], 'missed': [], 'neutral': []},
        'patchset': {'all': [], 'fixed': [], 'missed': [], 'neutral': []},
        'patch': {'all': [], 'fixed': [], 'missed': [], 'neutral': []},
        'comment': {'all': [], 'fixed': [], 'missed': [], 'neutral': []},
        'message': {'all': [], 'fixed': [], 'missed': [], 'neutral': []},
        'sentence': {'all': [], 'fixed': [], 'missed': [], 'neutral': []},
        'token': {'all': [], 'fixed': [], 'missed': [], 'neutral': []},
        'bug': {'all': [], 'fixed': [], 'missed': [], 'neutral': []},
        'vulnerability': {'all': [], 'fixed': [], 'missed': [], 'neutral': []}
    }

ALL_RIDS, FIXED_RIDS, MISSED_RIDS, NEUTRAL_RIDS, NM_RIDS, NF_RIDS, \
    FM_RIDS = ([],) * 7
ALL_MIDS, FIXED_MIDS, MISSED_MIDS, NEUTRAL_MIDS, NM_MIDS, NF_MIDS, \
    FM_MIDS = ([],) * 7
ALL_SIDS, FIXED_SIDS, MISSED_SIDS, NEUTRAL_SIDS, NM_SIDS, NF_SIDS, \
    FM_SIDS = ([],) * 7

TABLES = ['review', 'message', 'comment', 'patch', 'patchset', 'sentence',
          'token', 'bug', 'vulnerability']

def clear_objects():
    global OBJECTS
    OBJECTS = {
            'review': {'all': [], 'fixed': [], 'missed': [], 'neutral': []},
            'patchset': {'all': [], 'fixed': [], 'missed': [], 'neutral': []},
            'patch': {'all': [], 'fixed': [], 'missed': [], 'neutral': []},
            'comment': {'all': [], 'fixed': [], 'missed': [], 'neutral': []},
            'message': {'all': [], 'fixed': [], 'missed': [], 'neutral': []},
            'sentence': {'all': [], 'fixed': [], 'missed': [], 'neutral': []},
            'token': {'all': [], 'fixed': [], 'missed': [], 'neutral': []},
            'bug': {'all': [], 'fixed': [], 'missed': [], 'neutral': []},
            'vulnerability': {'all': [], 'fixed': [], 'missed': [], 'neutral': []}
        }

################################################################################
def query_by_year(year, table, ids=True):
    assert year in [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016]

    results = None
    if table == 'review':
        results = Review.objects.filter(created__year=year)
    elif table == 'message':
        results = Message.objects.filter(posted__year=year)
    elif table == 'patch':
        results = Patch.objects.filter(patchset__created__year=year)
    elif table == 'patchset':
        results = PatchSet.objects.filter(created__year=year)
    elif table == 'comment':
        results = Comment.objects.filter(patch__patchset__created__year=year)
    elif table == 'sentence':
        q1 = Q(comment__patch__patchset__review__created__year=year)
        q2 = Q(message__review__created__year=year)
        results = Sentence.objects.filter(q1 | q2)
    elif table == 'token':
        q1 = Q(sentence__comment__patch__patchset__review__created__year=year)
        q2 = Q(sentence__message__review__created__year=year)
        results = Token.objects.filter(q1 | q2)
    elif table in ['bug', 'vulnerability']:
        pass
    else:
        error("Table '" + str(table) + "' does not exist.")

    if not ids or results is None:
        return results
    else:
        return results.values_list('id', flat=True)

################################################################################
def query_all(table, ids=True):
    global OBJECTS
    results = None
    if table == 'review':
        if len(OBJECTS[table]['all']) != 0:
            results = OBJECTS[table]['all']
        else:
            results = Review.objects.all()
    elif table == 'patchset':
        if len(OBJECTS[table]['all']) != 0:
            results = OBJECTS[table]['all']
        else:
            results = PatchSet.objects.all()
    elif table == 'patch':
        if len(OBJECTS[table]['all']) != 0:
            results = OBJECTS[table]['all']
        else:
            results = Patch.objects.all()
    elif table == 'comment':
        if len(OBJECTS[table]['all']) != 0:
            results = OBJECTS[table]['all']
        else:
            results =  Comment.objects.all()
    elif table == 'message':
        if len(OBJECTS[table]['all']) != 0:
            results = OBJECTS[table]['all']
        else:
            results = Message.objects.all()
    elif table == 'sentence':
        if len(OBJECTS[table]['all']) != 0:
            results = OBJECTS[table]['all']
        else:
            results = Sentence.objects.all()
    elif table == 'token':
        if len(OBJECTS[table]['all']) != 0:
            results = OBJECTS[table]['all']
        else:
            results = Token.objects.all()
    elif table == 'bug':
        if len(OBJECTS[table]['all']) != 0:
            results = OBJECTS[table]['all']
        else:
            results = Bug.objects.all()
    elif table == 'vulnerability':
        if len(OBJECTS[table]['all']) != 0:
            results = OBJECTS[table]['all']
        else:
            results = Vulnerability.objects.all()
    else:
        error("Table '" + str(table) + "' does not exist.")
        return results

    OBJECTS[table]['all'] = results
    if not ids or results is None:
        return results
    else:
        return results.values_list('id', flat=True)

#### TF-IDF ####################################################################
def query_TF_dict(review_id, key='lemma'):
    """
    Returns the numerator of TF, the number of occurrences of the token in
    the review.
    """
    queryResults = Token.objects \
                        .filter(sentence__message__review__id=review_id) \
                        .values(key) \
                        .annotate(tf=Count(key))

    return queryResults

def query_DF(review_ids, key='lemma'):
    """
    Returns the denominator of DF, the number of documents in the population
    that contain the token at least once.
    """
    queryResults = None
    if key == 'token':
        queryResults = ReviewTokenView.objects \
            .filter(review_id__in=review_ids).values('token') \
            .annotate(df=Count('token')).order_by('-df')
    else:
        queryResults = ReviewLemmaView.objects \
            .filter(review_id__in=review_ids).values('lemma') \
            .annotate(df=Count('lemma')).order_by('-df')

    return queryResults

#### Complexity ################################################################
def query_rIDs_empty():
    """
    Return a list of review IDs that have messages containing a complexity
    field that has not been populated (denoted by '{}').
    """
    queryResults = Message.objects.filter(complexity__exact={}) \
        .values_list('review_id', flat=True)

    return queryResults

#### Messages ##################################################################
def query_mIDs(population):
    """ Passthrough function for determining which queries to run. """
    global ALL_MIDS, FIXED_MIDS, MISSED_MIDS, NEUTRAL_MIDS
    pop_dict = {'all': query_mIDs_all, 'fixed': query_mIDs_fixed,
                'missed': query_mIDs_missed, 'fm': query_mIDs_fm,
                'random': query_mIDs_random, 'nf': query_mIDs_nf,
                'nm': query_mIDs_nm, 'neutral': query_mIDs_neutral}

    ALL_MIDS = query_mIDs_all()
    FIXED_MIDS = query_mIDs_fixed()
    MISSED_MIDS = query_mIDs_missed()
    NEUTRAL_MIDS = list(set(ALL_MIDS) - set(FIXED_MIDS))
    NEUTRAL_MIDS = list(set(NEUTRAL_MIDS) - set(MISSED_MIDS))

    if population in pop_dict.keys():
        return pop_dict[population]()
    else:
        return query_mIDs_year(population)

def query_mIDs_all():
    """ Return a list of all message IDs. """
    global ALL_MIDS
    if len(ALL_MIDS) > 0:
        return ALL_MIDS

    queryResults = Message.objects.all().values_list('id', flat=True)
    ALL_MIDS = list(queryResults)

    return ALL_MIDS

def query_mIDs_random(message_ids, rand):
    """ Returns a list of all review IDs in the corpus. """
    queryResults = list(Message.objects.filter(id__in=message_ids) \
        .order_by('?').values_list('id', flat=True)[0:rand])

    return queryResults

def query_mIDs_fixed():
    """ Returns a list of message IDs that fixed a vulnerability. """
    global FIXED_MIDS
    if len(FIXED_MIDS) > 0:
        return FIXED_MIDS

    review_ids = query_rIDs_fixed()
    queryResults = Message.objects.filter(review_id__in=review_ids) \
        .values_list('id', flat=True)
    FIXED_MIDS = list(queryResults)

    return FIXED_MIDS

def query_mIDs_missed():
    """ Returns a list of message IDs that missed a vulnerability. """
    global MISSED_MIDS
    if len(MISSED_MIDS) > 0:
        return MISSED_MIDS

    review_ids = query_rIDs_missed()
    queryResults = Message.objects.filter(review_id__in=review_ids) \
        .values_list('id', flat=True)
    MISSED_MIDS = list(queryResults)

    return MISSED_MIDS

def query_mIDs_neutral():
    """
    Returns a list of message IDs that have not fixed or missed a vulnerability.
    """
    global NEUTRAL_MIDS
    if len(NEUTRAL_MIDS) > 0:
        return NEUTRAL_MIDS

    missed = query_mIDs_missed()
    fixed = query_mIDs_fixed()
    queryResults = Message.objects \
        .exclude(Q(id__in=missed) | Q(id__in=fixed)) \
        .values_list('id', flat=True)
    NEUTRAL_MIDS = list(queryResults)

    return NEUTRAL_MIDS

def query_mIDs_fm():
    """
    Returns a list of message IDs that have fixed or missed a vulnerability.
    """
    global FM_MIDS
    if len(FM_MIDS) > 0:
        return FM_MIDS

    missed = query_mIDs_missed()
    fixed = query_mIDs_fixed()
    queryResults = Message.objects \
        .filter(Q(id__in=missed) | Q(id__in=fixed)) \
        .values_list('id', flat=True)
    FM_MIDS = list(queryResults)

    return FM_MIDS

def query_mIDs_nf():
    """
    Returns a list of message IDs that have fixed a vulnerability or have not
    missed a vulnerability.
    """
    global NF_MIDS
    if len(NF_MIDS) > 0:
        return NF_MIDS

    missed = query_mIDs_missed()
    queryResults = Message.objects.exclude(id__in=missed) \
        .values_list('id', flat=True)
    NF_MIDS = list(queryResults)

    return NF_MIDS

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
    global NM_MIDS
    if len(NM_MIDS) > 0:
        return NM_MIDS

    fixed = query_mIDs_fixed()
    queryResults = Message.objects.exclude(id__in=fixed) \
        .values_list('id', flat=True)
    NM_MIDS = list(queryResults)

    return NM_MIDS

def query_mID_text(message_id):
    """ Return the text field of the given message. """
    queryResults = Message.objects.filter(id__exact=message_id) \
        .values_list('text', flat=True)

    return list(queryResults)[0] if len(list(queryResults)) > 0 else -1

#### Reviews ###################################################################
def query_rIDs(population):
    """ Passthrough function for determining which queries to run. """
    global ALL_RIDS, FIXED_RIDS, MISSED_RIDS, NEUTRAL_RIDS
    pop_dict = {'all': query_rIDs_all, 'fixed': query_rIDs_fixed,
                'missed': query_rIDs_missed, 'fm': query_rIDs_fm,
                'random': query_rIDs_random, 'nf': query_rIDs_nf,
                'nm': query_rIDs_nm, 'neutral': query_rIDs_neutral}

    ALL_RIDS = query_rIDs_all()
    FIXED_RIDS = query_rIDs_fixed()
    MISSED_RIDS = query_rIDs_missed()
    NEUTRAL_RIDS = list(set(ALL_RIDS) - set(FIXED_RIDS))
    NEUTRAL_RIDS = list(set(NEUTRAL_RIDS) - set(MISSED_RIDS))

    if population in pop_dict.keys():
        return pop_dict[population]()
    else:
        return query_rIDs_year(population)

def query_rIDs_all():
    """ Returns a list of all review IDs in the corpus. """
    global ALL_RIDS
    if len(ALL_RIDS) > 0:
        return ALL_RIDS
    queryResults = Review.objects.all().values_list('id', flat=True)

    ALL_RIDS = list(queryResults)

    return ALL_RIDS

def query_rIDs_random(review_ids, rand):
    """ Returns a list of all review IDs in the corpus. """
    queryResults = list(
            Review.objects.filter(id__in=review_ids)
            .order_by('?').values_list('id', flat=True)
        )
    return random.sample(queryResults, math.floor(len(queryResults) / rand))

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
    global FIXED_RIDS
    if len(FIXED_RIDS) > 0:
        return FIXED_RIDS

    queryResults = VulnerabilityBug.objects.distinct('bug__review__id') \
        .exclude(bug__review__id__exact=None) \
        .values_list('bug__review__id', flat=True)

    FIXED_RIDS = list(queryResults)

    return FIXED_RIDS

def query_rIDs_missed():
    """ Returns a list of review IDs that missed a vulnerability. """
    global MISSED_RIDS
    if len(MISSED_RIDS) > 0:
        return MISSED_RIDS

    queryResults = Review.objects.filter(missed_vulnerability=True) \
        .values_list('id', flat=True)

    MISSED_RIDS = list(queryResults)

    return MISSED_RIDS

def query_rIDs_neutral():
    """
    Returns a list of review IDs that have not fixed or missed a vulnerability.
    """
    global NEUTRAL_RIDS, ALL_RIDS, FIXED_RIDS, MISSED_RIDS
    if len(NEUTRAL_RIDS) > 0:
        return NEUTRAL_RIDS

    fixed = query_rIDs_fixed()
    missed = query_rIDs_missed()
    all = query_rIDs_all()

#    queryResults = Review.objects \
#        .exclude(Q(id__in=missed) | Q(id__in=fixed)) \
#        .values_list('id', flat=True)
#    NEUTRAL_RIDS = list(queryResults)

    NEUTRAL_RIDS = list(set(ALL_RIDS) - set(FIXED_RIDS))
    NEUTRAL_RIDS = list(set(NEUTRAL_RIDS) - set(MISSED_RIDS))

    return NEUTRAL_RIDS

def query_rIDs_fm():
    """
    Returns a list of review IDs that have fixed or missed a vulnerability.
    """
    global FM_RIDS
    if len(FM_RIDS) > 0:
        return FM_RIDS

    fixed = query_rIDs_fixed()
    missed = query_rIDs_missed()
    FM_RIDS = list(set(fixed) | set(missed))

    return FM_RIDS

def query_rIDs_nf():
    """
    Returns a list of review IDs that have fixed a vulnerability or have not
    missed a vulnerability.
    """
    global ALL_RIDS, NF_RIDS
    if len(NF_RIDS) > 0:
        return NF_RIDS

    missed = query_rIDs_missed()
    NF_RIDS = list(set(ALL_RIDS) - set(missed))

    return NF_RIDS

def query_rIDs_nm():
    """
    Returns a list of review IDs that have missed a vulnerability or have not
    fixed a vulnerability.
    """
    global ALL_RIDS, NM_RIDS
    if len(NM_RIDS) > 0:
        return NM_RIDS

    fixed = query_rIDs_fixed()
    NM_RIDS = list(set(ALL_RIDS) - set(fixed))

    return NM_RIDS

#### Sentences #################################################################
def query_sIDs_all():
    """ Returns a list of all sentence IDs in the corpus. """
    queryResults = Sentence.objects.all().values_list('id', flat=True)

    return queryResults

#### Tokens ####################################################################
def query_tokens(review_ids, key='lemma'):
    if key == 'lemma':
        queryResults = ReviewLemmaView.objects.distinct(key) \
            .filter(review_id__in=review_ids) \
            .values_list(key, flat=True)
    else:
        queryResults = ReviewTokenView.objects.distinct(key) \
            .filter(review_id__in=review_ids) \
            .values_list(key, flat=True)

    return queryResults

def query_tokens_all(key='lemma'):
    if key == 'lemma':
        queryResults = ReviewLemmaView.objects.distinct(key) \
            .values_list(key, flat=True)
    else:
        queryResults = ReviewTokenView.objects.distinct(key) \
            .values_list(key, flat=True)

    return queryResults

def query_top_x_tokens(review_ids, x, key='lemma'):
    message_ids = Message.objects.distinct('id') \
        .filter(review_id__in=review_ids) \
        .values_list('id', flat=True)

    queryResults = Token.objects \
        .filter(sentence__message__review__id__in=review_ids) \
        .filter(token__iregex=r"\w+") \
        .values(key) \
        .annotate(freq=Count(key)) \
        .order_by('-freq') \
        .values_list(key, flat=True)

    return queryResults[0:x]
