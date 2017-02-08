"""
@AUTHOR: meyersbs
"""

from django.contrib.postgres import fields
from django.db import connection
from django.db.models import Count
from app.models import *


def _custom_raw_review_token(population):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT t.token AS id, COUNT(t.review_id) AS df "
        "FROM public.vw_review_token t "
        "WHERE t.review_id IN " + str(population) + " "
        "GROUP BY t.token")

#    print(cursor.fetchone())
    df_dict = {}
    for entry in cursor.fetchall():
#        print(entry)
        df_dict[entry.id] = entry.df

    return df_dict


def query_TF_dict(reviewID, lemma="token"):
    """
    Returns a dictionary with each key being a token in the review and the
    value being the TF calculation:
    TF = (# of occurrences of Token in Review)/(# of total tokens in Review)
    """
    innerQuery = (
        "(SELECT SUM(t.frequency) FROM public.token t "
        "JOIN public.message m ON m.id = t.message_id "
        "WHERE m.review_id=" + str(reviewID) + ") "
        )
    queryResults = Token.objects.raw(
        "SELECT t.id, t." + str(lemma) + ", ((SUM(t.frequency)*1.0) / "
        + innerQuery + ") AS tf "
        "FROM public.token t JOIN public.message m "
        "ON m.id=t.message_id WHERE m.review_id=" + str(reviewID) + " "
        "GROUP BY t.token, t.id"
        )
    termFrequencyDict = {}
    for entry in queryResults:
        # For whatever reason, this query returns tf as a decimal.Decimal
        # objects, so we need to cast it to a float in order for it to be
        # useful.
        termFrequencyDict[entry.token] = float(entry.tf)

    return termFrequencyDict

def query_DF_dict(lemma="token", population=[]):
    """
    Returns a dictionary where each key is a token (or lemma) and each value is
    the Document Frequency (DF) associated with that token.
    """
    if population == []:
        raise ValueError("Received invalid population for IDF query.")

    # We have to cast the list of IDs to a tuple so that when we concatenate
    # the list with the query, the string representation of the list is
    # (rID1, rID2,...) instead of [rID1, rID2...]
    population = tuple(population)

#    print(population)
#    print(type(population))

    documentFrequencies = {}
    if lemma == "token":
        queryResults = (ReviewTokenView.objects
            .values('token', 'review_id')
            .annotate(df=Count('review_id')))
#            .filter(review_id__in=population))
#        documentFrequencies = _custom_raw_review_token(population)
    elif lemma == "lemma":
        queryResults = ReviewLemmaView.objects.raw(
            "SELECT t.lemma AS id, COUNT(t.review_id) AS df "
            "FROM public.vw_review_lemma t "
            "WHERE t.review_id IN " + str(population) + " "
            "GROUP BY t.lemma")
    else:
        return documentFrequencies

    print("LEN: " + str(len(queryResults)))
#    print(queryResults)

    for entry in queryResults:
#        print(entry)
        if entry['review_id'] in population:
            documentFrequencies[entry['token']] = entry['df']

    print("LEN2: " + str(len(documentFrequencies)))
#    print(documentFrequencies)
    return documentFrequencies

def query_rIDs_by_year(year):
    """
    Returns a list of Review.id where Review.created is within the
    specified year.
    """
    queryResults = Review.objects.raw(
        "SELECT public.review.id FROM public.review "
        "WHERE to_char(public.review.created, \'YYYY\')::text=\'"
        + str(year) + "\'")

    reviewIDs = [ entry.id for entry in queryResults ]
    return reviewIDs

def query_rIDs_all():
    """ Returns a list of all Review IDS within the database. """
    queryResults = Review.objects.raw(
        "SELECT public.review.id FROM public.review "
        "ORDER BY public.review.id ASC")

    reviewIDs = [ entry.id for entry in queryResults ]
    return reviewIDs

def query_rIDs_fixed():
    """ Returns a list of reviewIDs that fixed a vulnerability. """
    queryResults = ReviewBug.objects.raw(
        "SELECT DISTINCT t.review_id, t.id FROM public.review_bug t "
        "JOIN public.vulnerability v ON t.bug_id=v.bug_id "
        "ORDER BY t.review_id ASC")

    reviewIDs = [ entry.id for entry in queryResults ]
    return reviewIDs

def query_rIDs_missed():
    """ Returns a list of reviewIDs that missed a vulnerability. """
    queryResults = Review.objects.raw(
        "SELECT public.review.id FROM public.review "
        "WHERE public.review.missed_vulnerability=True "
        "ORDER BY public.review.id ASC")

    reviewIDs = [ entry.id for entry in queryResults ]
    return reviewIDs

#### OLD STUFF ####

def queryMessagesByYear(year):
    """
    Returns a list of Message objects where Message.posted contains year.
    """
    queryResults = Message.objects.raw(
        "SELECT * FROM public.message "
        "WHERE to_char(public.message.posted, \'YYYY\')::text=\'" + str(year) + "\'")

    messages = []
    for entry in queryResults:
        messages.append(entry)

    return messages

def __queryMessagesByReview(reviewID):
    """
    Returns a list of Message objects where Message.review_id=reviewID.
    """
    queryResults = Message.objects.raw(
        "SELECT public.message.id FROM public.message "
        "WHERE public.message.review_id=" + str(reviewID))

    messages = []
    for entry in queryResults:
        messages.append(entry)

    return messages

def __queryTokenCountByReview(reviewID):
    """
    Returns the number of tokens in all of the messages where Message.review_id
    =reviewID.
    """
    messages = __queryMessagesByReview(reviewID)

    numTokens = 0
    for message in messages:
        numTokens += __queryTokenCountByMessage(message.id)

    return numTokens

def __queryTokenCountByMessage(messageID):
    """
    Returns the number of tokens in a single message where Message.id=messageID.
    """
    queryResults = Message.objects.raw(
        "SELECT public.token.id, public.token.frequency "
        "FROM public.token JOIN public.message "
        "ON public.token.message_id=public.message.id "
        "WHERE public.message.id=" + str(messageID))

    numTokens = 0
    for entry in queryResults:
        numTokens += entry.frequency

    return numTokens

