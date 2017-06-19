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

    def get_bugs(self, year):
        """
        Return a list of bugs that were associated with the specified year.
        """
        bugs = list()
        directory = self.get_bugs_path(year)
        for path in self._get_files(directory, pattern='bugs.csv'):
            with open(path, 'r') as file:
                file.readline()  # Skip header
                reader = csv.reader(file)
                for row in reader:
                    bugs.append(self._to_dict(row))
        return bugs

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

    def save_reviews(self, year, chunk, reviews, errors=None):
        """
        Save the specified reviews to a json file in the reviews path
        associated with the specified year. Format according to the specified
        chunk. Log errors in a CSV file in the same directory.
        """
        directory = self.get_reviews_path(year)
        if not os.path.exists(directory):
            os.mkdir(directory, mode=0o755)

        path = os.path.join(directory, 'reviews.{}.json'.format(chunk))
        with open(path, 'w') as file:
            json.dump(reviews, file)

        if errors:
            path = os.path.join(directory, 'errors.csv'.format(index))
            with open(path, 'a') as file:
                writer = csv.writer(file)
                writer.writerows([(error,) for error in errors])
        return path

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

    # TODO: Remove function once bug information is available in JSON format
    def _to_dict(self, row):
        """
        The monorail API is awful, and our credentials don't work. So this
        function grabs the CSV file, adds a few keys, and converts everything
        into json.
        """
        bug = dict()

        bug['id'] = row[0]
        bug['type'] = row[1]
        bug['cve'] = row[2]
        bug['status'] = row[3]
        bug['opened'] = row[4]
        bug['closed'] = row[6]
        bug['modified'] = row[8]
        bug['summary'] = row[10]
        bug['labels'] = row[11]

        return bug
