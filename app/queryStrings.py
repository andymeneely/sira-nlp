"""
@AUTHOR: meyersbs
"""

from django.contrib.postgres import fields
#from django.db import models
from app.models import *

def queryTermFrequency(token, reviewID):
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
        "WHERE public.token.text=\'" + token + "\' " \
        "AND public.review.id=" + str(reviewID) + " " \
        "GROUP BY public.token.id, public.review.id")

    # This doesn't work because len() is not defined for RawQuerySet
    # termFrequency = len(queryResults)
    # print(termFrequency)

    termFrequency = 0;
    for entry in queryResults:
        termFrequency += 1

    return termFrequency

def queryDocumentFrequency(token, year=None):
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
            "WHERE public.token.text=\'" + token + "\' " \
            "AND to_char(public.review.created, \'YYYY\')::text=\'" \
            + str(year) + "\'")
    else:
        queryResults = Message.objects.raw(
            "SELECT DISTINCT(public.message.review_id), " \
            "public.message.id FROM public.message " \
            "JOIN public.token " \
            "ON public.message.id=public.token.message_id " \
            "WHERE public.token.text=\'" + token + "\'")

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
