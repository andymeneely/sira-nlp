"""
@AUTHOR: nuthanmunaiah
@AUTHOR: meyersbs
"""

import csv
import glob
import json
import os

from app.lib import helpers


class Files(object):
    """

    """
    def __init__(self, settings):
        """
        Constructor.
        """
        self.bugs_path = settings.BUGS_PATH
        self.ids_path = settings.IDS_PATH
        self.reviews_path = settings.REVIEWS_PATH
        self.vulnerabilities_path = settings.VULNERABILITIES_PATH
        self.bots = settings.BOTS

    def get_bug(self, id, year=None):
        """Retrieve a bug identified by the unique identifier specified.

        Parameters
        ----------
        id : int
            Unique identifier of the bug to retrieve.

        Returns
        -------
        bug : dict
            Bug identified by the identifier specified. An exception is raised
            when no bug was found.
        """
        year = self.get_year(id, switch='bugs') if year is None else year
        directory = self.get_bugs_path(year)
        for path in self._get_files(directory, pattern='bugs.*.json'):
            bugs = helpers.load_json(path, sanitize=False)
            for bug in bugs:
                if id == bug['id']:
                    return bug
        raise Exception('No bug identified by {}'.format(id))

    def get_bugs(self, year):
        """Yield bugs that were published in a specified year.

        Parameters
        ----------
        year : int
            Bugs published in the specified year must be returned.

        Return
        ------
        bugs : generator
            Iterator-like object that allows iteration over the bugs being
            returned without blocking the caller.
        """
        directory = self.get_bugs_path(year)
        for path in self._get_files(directory, pattern='bugs.*.json'):
            for bug in helpers.load_json(path):
                yield bug

    def get_bugs_path(self, year):
        """
        Return the system path for the bugs associated with the specified year.
        """
        return self.bugs_path.format(year=year)

    def get_ids(self, year, switch):
        """
        Return the IDs associated with the specified year.
        """
        ids = list()
        path = os.path.join(self.get_ids_path(switch), '{}.csv'.format(year))
        with open(path, 'r') as file:
            reader = csv.reader(file)
            ids = [row[0] for row in reader]
        return ids

    def get_ids_path(self, switch):
        '''Return path to files containing review or bug identifiers.'''
        if switch not in ['bugs', 'reviews']:
            raise ValueError('Argument switch must be \'bugs\' or \'reviews\'')
        return self.ids_path.format(switch=switch)

    def get_messages(self, id, year=None, clean=False):
        """
        Given a review ID, return a list of messages associated with that
        review.
        """
        year = self.get_year(id, switch='reviews') if year is None else year
        review = self.get_review(id, year)
        messages = list()
        for message in review['messages']:
            sender = message['sender']
            if sender in self.bots:
                continue
            text = helpers.clean(message['text']) if clean else message['text']
            messages.append((sender, text))
        return messages

    def get_description(self, id, year=None):
        """
        Given a review ID, return the description associated with that review.
        """
        year = self.get_year(id, switch='reviews') if year is None else year
        review = self.get_review(id, year)
        return review['description']

    def get_review(self, id, year=None):
        """

        """
        year = self.get_year(id, switch='reviews') if year is None else year
        directory = self.get_reviews_path(year)
        for path in self._get_files(directory, pattern='reviews.*.json'):
            reviews = helpers.load_json(path)
            for review in reviews:
                if id == review['issue']:
                    return review
        raise Exception('No code review identified by {}'.format(id))

    def get_reviews(self, year):
        """
        Yield the reviews associated with the specified year.
        """
        directory = self.get_reviews_path(year)
        for path in self._get_files(directory, pattern='reviews.*.json'):
            for review in helpers.load_json(path):
                yield review

    def get_reviews_path(self, year):
        """
        Return the system path for the reviews associated with the specified
        year.
        """
        return self.reviews_path.format(year=year)

    def get_vulnerabilities(self):
        """
        Return a list of all vulnerabilities.
        """
        vulnerabilities = list()
        for path in self._get_files(self.vulnerabilities_path, '*.csv'):
            (source, _) = os.path.splitext(os.path.basename(path))
            with open(path, 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    vulnerabilities.append((source, row[0], row[1]))
        return vulnerabilities

    def get_year(self, id, switch):
        """

        """
        paths = self._get_files(self.get_ids_path(switch), '*.csv')
        for path in paths:
            ids = None
            with open(path, 'r') as file:
                reader = csv.reader(file)
                ids = [int(row[0]) for row in reader]
            if ids is not None and id in ids:
                return os.path.basename(path).replace('.csv', '')
        raise Exception('No code review or bug identified by {}'.format(id))

    def save_ids(self, year, ids, switch):
        """
        Save the specified IDs to a file in the path associated with the
        specified year.
        """
        path = os.path.join(self.get_ids_path(switch), '{}.csv'.format(year))
        with open(path, 'a') as file:
            writer = csv.writer(file)
            writer.writerows([(id,) for id in ids])
        return path

    def save_bugs(self, year, chunk, bugs, errors=None):
        """Save bugs to a JSON file and errors (if any) to a CSV file.

        Parameters
        ----------
        year : int
            Year in which the bugs contained in the |bugs| argument were
            published.
        chunk : int
            Identifier of the chunk to which the bugs contained in the |bugs|
            argument belong to.
        bugs : list(dict)
            List of bugs to be saved.
        errors : list(int), optional
            List of unique identifiers of bugs that could not be retrieved.
        """
        directory = self.get_bugs_path(year)
        return self._save(directory, chunk, bugs, errors, switch='bugs')

    def save_reviews(self, year, chunk, reviews, errors=None):
        """Save reviews to a JSON file and errors (if any) to a CSV file.

        Parameters
        ----------
        year : int
            Year in which the code reviews contained in the |reviews| argument
            were created.
        chunk : int
            Identifier of the chunk to which the code reviews contained in the
            |reviews| argument belong to.
        reviews : list(dict)
            List of reviews to be saved.
        errors : list(int), optional
            List of unique identifiers of code reviews that could not be
            retrieved.
        """
        directory = self.get_reviews_path(year)
        return self._save(directory, chunk, reviews, errors, switch='reviews')

    def stat_review(self, id):
        """
        Return a dictionary of the fields associated with the the specified
        review ID.
        """
        stats = dict()
        review = self.get_review(id)
        stats['status'] = 'Closed' if review['closed'] else 'Open'
        stats['created'] = review['created']
        stats['reviewers'] = len(review['reviewers'])
        stats['messages'] = len(review['messages'])
        stats['patchsets'] = len(review['patchsets'])
        return stats

    def stat_reviews(self, year):
        """
        Return a dictionary of fields for all of the reviews associated with
        the specified year.
        """
        stats = dict()
        reviews = list(self.get_reviews(year))
        stats['reviews'] = len(reviews)
        stats['open'] = len(
                [review['issue'] for review in reviews if not review['closed']]
            )
        (messages, comments, patchsets) = (dict(), dict(), dict())
        for review in reviews:
            id = review['issue']
            messages[id] = len(review['messages'])
            patchsets[id] = len(review['patchsets'])
            comments[id] = 0
            for patchset in review['patchsets'].values():
                comments[id] += patchset['num_comments']
        stats['messages'] = helpers.sort(messages, desc=True)
        stats['comments'] = helpers.sort(comments, desc=True)
        stats['patchsets'] = helpers.sort(patchsets, desc=True)
        return stats

    def transform_bug(self, bug):
        """Transform bug JSON to add a list of participants.

        Parameters
        ----------
        bug: dict
            A JSON representation of a Chromium bug downloaded from Monorail.
            The JSON has a key---comments---that contains conversation between
            developers triaging the bug.

        Returns
        -------
        bug: dict
            A transformed bug JSON which has two additional keys added, they
            are:

           (1) participants: The corresponding value is a list of email
               address of developers who participated in the bug by being on
               cc.
           (2) contributors: The corresponding value is a list of email
               address of developers who have contributed, through non-empty
               comments, to the process of triaging of bug.
        """
        participants = set()
        if 'cc' in bug:
            for developer in bug['cc']:
                participants.add(developer['name'])

        contributors = set()
        for comment in bug['comments']:
            author = comment['author']['name']
            if author in contributors or author in self.bots:
                continue
            if comment['content']:
                contributors.add(comment['author']['name'])

        bug['participants'] = list(participants)
        bug['contributors'] = list(contributors)

        return bug

    def transform_review(self, review):
        """

        """
        patchsets = review['patchsets']

        reviewed_files = set()
        for (_, patchset) in patchsets.items():
            for file in patchset['files']:
                reviewed_files.add(file)

        patchsets = helpers.sort(patchsets, by='key', cast=int, desc=True)
        committed_files = None
        for (_, patchset) in patchsets.items():
            committed_files = set(list(patchset['files'].keys()))
            break

        review['reviewed_files'] = list(reviewed_files)
        review['committed_files'] = list(committed_files)

        return review

    # Private Members

    def _get_files(self, path, pattern):
        """
        Return a list of files within the specified path that match the
        specified pattern.
        """
        files = [
                os.path.join(path, file)
                for file in glob.glob(os.path.join(path, pattern))
            ]
        return files

    def _parse(self, commit):
        """

        """
        pass

    def _save(self, directory, chunk, items, errors, switch):
        """
        Save the specified reviews to a json file in the reviews path
        associated with the specified year. Format according to the specified
        chunk. Log errors in a CSV file in the same directory.
        """
        if not os.path.exists(directory):
            os.mkdir(directory, mode=0o755)

        path = os.path.join(directory, '{}.{}.json'.format(switch, chunk))
        with open(path, 'w') as file:
            json.dump(items, file)

        if errors:
            path = os.path.join(directory, 'errors.csv')
            with open(path, 'a') as file:
                writer = csv.writer(file)
                writer.writerows([(error,) for error in errors])
        return path
