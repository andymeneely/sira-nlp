import multiprocessing

from apiclient.discovery import build
from googleapiclient.errors import HttpError
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials as SAC

from app.lib.helpers import *
from app.lib.logger import *

__all__ = ['Monorail']

SCOPES = ['https://www.googleapis.com/auth/userinfo.email']
MAX_RESULTS = 1000
MAX_RETRIES = 3


class Monorail(object):
    '''Interface to the Google Monorail Service.

    Parameters
    ----------
    url : string
        URL to the Monorail API instance.
    keyfile : string
        Path to a JSON-formatted keyfile typically containing a PKCS8 key used
        to authenticate server to the Monorail API using  OAuth 2.0. See
        https://developers.google.com/identity/protocols/OAuth2ServiceAccount
        for more information on creating a service account for server-to-server
        access using OAuth 2.0.
    '''
    def __init__(self, url, keyfile):
        self.url = url
        self.credentials = SAC.from_json_keyfile_name(keyfile, SCOPES)

    def get_bug(self, id):
        '''Retrieve bug identified by the unique identifier specified.

        Parameters
        ----------
        id : int
            Unique identifier of the bug to retrieve.

        Returns
        -------
        bug : dict
            Bug identified by the identifier specified. None is returned if no
            bug was found or an error occurred when retrieving the bug.
        '''
        return self._get_bug(id)

    def get_bugs(self, ids, processes):
        '''Retrieve bugs identified by unique identifiers specified.

        Parameters
        ----------
        ids : list(int)
            List of unique identifier of bugs to retrieve.
        processes : int
            Number of processes to spawn when retrieving bugs in parallel

        Returns
        -------
        bugs : list(dict)
            List of dictionaries each representing a bug identified by one of
            the unique identifiers specified.
        errors : list(int)
            List of unique identifiers of those bugs that were either not found
            or an error occurred when retrieving the bug.
        '''
        manager = multiprocessing.Manager()
        bugs = manager.Queue(len(ids))
        errors = manager.Queue()
        lock = manager.Lock()

        with multiprocessing.Pool(processes) as pool:
            pool.starmap(
                    self._put_bug, [(id, bugs, errors, lock) for id in ids]
                )

        return (to_list(bugs), to_list(errors))

    def _get_bug(self, id, lock=None):
        '''Retrieve bug identified by the unique identifier specified.

        The process of retrieving a bug involves two steps: retrieval of bug
        metadata and retrieval of comments made on the bug. This method
        implements the two steps.
        '''
        bug = None

        service = self._get_service(lock)
        request = service.issues().get(projectId='chromium', issueId=id)
        response = self._get_response(request)
        if response is not None:
            comments = self._get_comments(id)
            if comments is not None:
                bug = response
                bug['comments'] = comments

        return bug

    def _get_comments(self, bug_id):
        '''Retrieve comments made to a bug.'''
        comments = list()

        num_comments = self._get_numcomments(bug_id)
        index = 0
        while True:
            _comments = self.__get_comments(bug_id, index)
            if _comments is None:
                return None
            comments.extend(_comments)
            debug('[{}] {}/{}'.format(bug_id, len(comments), num_comments))
            if len(comments) == num_comments:
                break
            index += MAX_RESULTS

        return comments

    def __get_comments(self, bug_id, index):
        '''Retrieve comments made to a bug starting at specified index.

        The results in the response from certain Monorail service methods are
        paginated and self._get_comments invokes this method to retrieve a page
        of comments made to a bug.
        '''
        service = self._get_service()
        request = service.issues().comments().list(
                projectId='chromium', issueId=bug_id,
                maxResults=MAX_RESULTS, startIndex=index
            )
        response = self._get_response(request)
        return [comment for comment in response['items']] if response else None

    def _get_numcomments(self, bug_id):
        '''Retrieve the number of comments made to a bug.'''
        service = self._get_service()
        request = service.issues().comments().list(
                projectId='chromium', issueId=bug_id,
                maxResults=MAX_RESULTS, startIndex=0
            )
        response = self._get_response(request)
        if response is None:
            raise Exception('No response from Monorail API despite retries.')
        return response['totalResults']

    def _get_response(self, request):
        '''Execute a HTTP request and return the response.'''
        debug(request.uri)
        attempt = 1
        while attempt <= MAX_RETRIES:
            try:
                return request.execute()
            except HttpError as exception:
                debug(exception.args)
                warning('{}/{} {}'.format(attempt, MAX_RETRIES, request.uri))
                sleep(1)
                attempt += 1
        error('Failed {}'.format(request.uri))
        return None

    def _get_service(self, lock=None):
        '''Create and return an instance of the Monorail API service client.'''
        http = Http()
        if self.credentials.access_token_expired:
            if lock is not None:
                with lock:
                    self.credentials.refresh(http)
            else:
                self.credentials.refresh(http)
        http = self.credentials.authorize(http)
        return build('monorail', 'v1', http=http, discoveryServiceUrl=self.url)

    def _put_bug(self, id, bugs, errors, lock):
        '''Retrieve a bug and put it into the bugs queue.

        When retrieving bugs in parallel, each process invokes this method to
        retrieve a single bug. If the bug retrieval was successful, it is put
        into bugs else errors, both of which are shared queues.
        '''
        bug = self._get_bug(id, lock)
        if bug is not None:
            bugs.put(bug, block=True)
        else:
            errors.put(id, block=True)
