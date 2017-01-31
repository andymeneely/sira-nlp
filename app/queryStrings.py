"""
@AUTHOR: meyersbs
"""

from django.contrib.postgres import fields
#from django.db import models
from app.models import *

def _queryMessagesByReview(reviewID):
    """
    Returns a list of Message objects where Message.review_id=reviewID.
    """
    queryResults = Message.objects.raw(
        "SELECT public.message.id FROM public.message " \
        "WHERE public.message.review_id=" + str(reviewID))

    messages = []
    for entry in queryResults:
        messages.append(entry)

    return messages

def _queryTokenCountByReview(reviewID):
    """
    Returns the number of tokens in all of the messages where Message.review_id
    =reviewID.
    """

    messages = _queryMessagesByReview(reviewID)

    numTokens = 0
    for message in messages:
        query = Token.objects.raw(
                    "SELECT public.token.id, public.token.frequency FROM public.token " \
                    "JOIN public.message " \
                    "ON public.message.id=public.token.message_id " \
                    "WHERE public.message.id=" + str(message.id))
        for entry in query:
            numTokens += entry.frequency

    return numTokens


def queryTermFrequency(token, reviewID, lemma="text"):
    """
    Returns the number of occurences of the specified token in the specified
    reviewID.
    """
    queryResults = Token.objects.raw(
        "SELECT public.token.id, COUNT(public.token.frequency) " \
        "FROM public.token " \
        "JOIN public.message " \
        "ON public.message.id=public.token.message_id " \
	"JOIN public.review " \
	"ON public.review.id=public.message.review_id " \
        "WHERE public.token." + lemma + "=\'" + token + "\' " \
        "AND public.review.id=" + str(reviewID) + " " \
        "GROUP BY public.token.id, public.review.id")

    numTokens = _queryTokenCountByReview(reviewID)

    # This doesn't work because len() is not defined for RawQuerySet
    # termFrequency = len(queryResults)
    # print(termFrequency)

    termFrequency = 0;
    for entry in queryResults:
        termFrequency += 1

    return float(termFrequency)/float(numTokens) if numTokens != 0 else 0

def queryDocumentFrequency(token, year=None, lemma="text"):
    """
    Returns the total number of documents containing the specified token if
    year==None. Otherwise, returns the total number of documents within that
    year containing the specified token.
    """
    queryResults = None
    if year is not None:
        queryResults = Message.objects.raw(
            "SELECT DISTINCT(public.message.review_id), " \
            "public.message.id FROM public.message " \
            "JOIN public.token " \
            "ON public.message.id=public.token.message_id " \
            "JOIN public.review " \
            "ON public.review.id=public.message.review_id " \
            "WHERE public.token." + lemma + "=\'" + token + "\' " \
            "AND to_char(public.review.created, \'YYYY\')::text=\'" \
            + str(year) + "\'")
    else:
        queryResults = Message.objects.raw(
            "SELECT DISTINCT(public.message.review_id), " \
            "public.message.id FROM public.message " \
            "JOIN public.token " \
            "ON public.message.id=public.token.message_id " \
            "WHERE public.token." + lemma + "=\'" + token + "\'")

    reviews = []
    for entry in queryResults:
        reviews.append(entry.review_id)

    return len(set(reviews))

def queryTotalDocuments(year=None):
    """
    Returns the total number of documents in the database if year==None.
    Otherwise, returns the total number of documents within that year.
    """
    if year is not None:
        return len(queryReviewsByYear(year))
    else:
        queryResults = Review.objects.all()
        cnt = 0
        for entry in queryResults:
            cnt += 1

        return cnt

def queryReviewsByYear(year):
    """
    Returns a list of Review.id where Review.created is within the
    specified year.
    """
    queryResults = Review.objects.raw(
        "SELECT public.review.id " \
        "FROM public.review " \
        "WHERE to_char(public.review.created, \'YYYY\')::text=\'" \
        + str(year) + "\'")

    reviewIDs = []
    for entry in queryResults:
        reviewIDs.append(entry.id)

    return reviewIDs
