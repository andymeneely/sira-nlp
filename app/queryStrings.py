"""
@AUTHOR: meyersbs
"""

from django.contrib.postgres import fields

from app.models import *

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

def queryTermFrequency(token, reviewID, lemma="text"):
    """
    Returns the number of occurences of the specified token in the specified
    reviewID.
    """
    queryResults = Token.objects.raw(
        "SELECT public.token.id, COUNT(public.token.frequency) "
        "FROM public.token "
        "JOIN public.message "
        "ON public.message.id=public.token.message_id "
	"JOIN public.review "
	"ON public.review.id=public.message.review_id "
        "WHERE public.token." + lemma + "=\'" + token + "\' "
        "AND public.review.id=" + str(reviewID) + " "
        "GROUP BY public.token.id, public.review.id")

    numTokens = __queryTokenCountByReview(reviewID)

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
            "SELECT DISTINCT(public.message.review_id), "
            "public.message.id FROM public.message "
            "JOIN public.token "
            "ON public.message.id=public.token.message_id "
            "JOIN public.review "
            "ON public.review.id=public.message.review_id "
            "WHERE public.token." + lemma + "=\'" + token + "\' "
            "AND to_char(public.review.created, \'YYYY\')::text=\'"
            + str(year) + "\'")
    else:
        queryResults = Message.objects.raw(
            "SELECT DISTINCT(public.message.review_id), "
            "public.message.id FROM public.message "
            "JOIN public.token "
            "ON public.message.id=public.token.message_id "
            "WHERE public.token." + lemma + "=\'" + token + "\'")

    reviews = []
    for entry in queryResults:
        reviews.append(entry.review_id)

    return len(set(reviews))

def queryReviewsByYear(year):
    """
    Returns a list of Review.id where Review.created is within the
    specified year.
    """
    queryResults = Review.objects.raw(
        "SELECT public.review.id FROM public.review "
        "WHERE to_char(public.review.created, \'YYYY\')::text=\'"
        + str(year) + "\'")

    reviewIDs = []
    for entry in queryResults:
        reviewIDs.append(entry.id)

    return reviewIDs, len(reviewIDs)

def queryAllReviews():
    """
    Returns a list of all Review IDS within the database.
    """
    queryResults = Review.objects.raw(
        "SELECT public.review.id FROM public.review "
        "ORDER BY public.review.id ASC")

    #print(queryResults)

    reviewIDs = []
    for entry in queryResults:
        reviewIDs.append(entry.id)

    #print(reviewIDs)
    return reviewIDs, len(reviewIDs)
