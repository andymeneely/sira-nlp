"""
@AUTHOR: nuthanmunaiah
"""

import csv
import multiprocessing
import os

from requests import get, exceptions

from app.lib.helpers import *
from app.lib.logger import *

# Rietveld is where reviews get pulled from.
__all__ = ['Rietveld']

CREATED_AFTER = '{}-01-01 00:00:00'
CREATED_BEFORE = '{}-12-31 11:59:59'

BASE_URL = 'https://codereview.chromium.org'
SEARCH_URL = BASE_URL + '/search'
REVIEW_URL = BASE_URL + '/api' + '/{rid}'
PATCHSET_URL = REVIEW_URL + '/{psid}'

STATUS_OK = 200


class Rietveld(object):
    """
    A collection of helper functions for retrieving code reviews from chromium
    and parsing them.
    """
    def get_ids(self, year):
        """
        Return a list of all of the IDs associated with reviews created in the
        specified year.
        """
        ids = list()

        parameters = {
                'format': 'json', 'limit': '1000', 'keys_only': True,
                'cursor': '', 'created_after': CREATED_AFTER.format(year),
                'created_before': CREATED_BEFORE.format(year)
            }

        while True:
            (status, _ids, cursor) = self._get_ids(parameters)

            if status != 0:
                error('Retrieval of code review identifiers failed.')
                break

            if cursor == '':
                debug('Retrieved code review identifiers for {}'.format(year))
                break

            ids += _ids
            parameters['cursor'] = cursor

        return ids

    def get_reviews(self, ids, processes):
        """
        Get all of the reviews associated with the specified IDs. Return a
        tuple of the form: ([rev1, rev2,...revN], [err1, err2,...errN])
        """
        manager = multiprocessing.Manager()
        reviews = manager.Queue(len(ids))
        errors = manager.Queue()

        with multiprocessing.Pool(processes) as pool:
            pool.starmap(
                    self._put_review, [(id, reviews, errors) for id in ids]
                )

        return (to_list(reviews), to_list(errors))

    def _get_ids(self, parameters):
        """
        Given a specified list of parameters, form a query and return the
        results as a tuple of the form (a, b, c), where a is the status of the
        query, b is a json object containing the results of the query, and c
        is a json object containing the cursor of the query.
        """
        (status, ids, cursor) = (-1, None, None)

        url = SEARCH_URL
        debug('{}?{}'.format(url, to_querystring(parameters)))
        try:
            (scode, json) = get_json(url, parameters)
            if scode == STATUS_OK:
                status = 0
                (ids, cursor) = (json['results'], json['cursor'])
                sleep(seconds=10)
            else:
                error('[HTTP {}] {}?{}'.format(
                        scode, url, to_querystring(parameters)
                    ))
        except exceptions.RequestException as exception:
            error('{}\n{}'.format(exception.request.url, exception))

        return (status, ids, cursor)

    def _put_review(self, rid, reviews, errors):
        """
        Grab the review associated with the specified ID, create a dictionary
        of patchsets associated with that review, and append the review with
        its patchsets to the specified list of reviews.
        """
        url = REVIEW_URL.format(rid=rid)
        debug(url)
        try:
            (scode, review) = get_json(url, parameters={'messages': True})
            if scode == STATUS_OK:
                patchsets = dict()
                for psid in review['patchsets']:
                    (status, patchset) = self._get_patchset(rid, psid)
                    if status == 0:
                        patchsets[psid] = patchset
                    else:
                        patchsets = None
                        errors.put(rid, block=True)
                        break

                if patchsets is not None and len(patchsets) > 0:
                    review['patchsets'] = patchsets
                    reviews.put(review, block=True)

                sleep(seconds=10)
            else:
                error('[HTTP {}] {}'.format(scode, url))
                errors.put(rid, block=True)
        except exceptions.RequestException as exception:
            error('{}\n{}'.format(exception.request.url, exception))
            errors.put(rid, block=True)

    def _get_patchset(self, rid, psid):
        """
        Get the patchset associated with the specified patchset ID within the
        specified review ID.
        """
        (status, patchset) = (-1, None)
        url = PATCHSET_URL.format(rid=rid, psid=psid)
        debug(url)
        try:
            (scode, patchset) = get_json(url, parameters={'comments': True})
            if scode == STATUS_OK:
                status = 0
                sleep(seconds=1)
            else:
                error('[HTTP {}] {}'.format(scode, url))
        except exceptions.RequestException as exception:
            error('{}\n{}'.format(exception.request.url, exception))

        return (status, patchset)
