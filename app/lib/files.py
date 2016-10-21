import csv
import glob
import json
import os

from app.lib import helpers



class Files(object):
    def __init__(self, settings):
        self.bugs_path = settings.BUGS_PATH
        self.ids_path = settings.IDS_PATH
        self.reviews_path = settings.REVIEWS_PATH
        self.bots = settings.BOTS

    def get_bugs(self, year):
        bugs = None
        directory = self.get_bugs_path(year)
        for path in self._get_files(directory, pattern='bugs.csv'):
            with open(path, 'r') as file:
                file.readline()  # Skip header
                if bugs is None:
                    bugs = list()
                reader = csv.reader(file)
                for row in reader:
                    bugs.append(self._to_dict(row))
        return bugs

    def get_bugs_path(self, year):
        return self.bugs_path.format(year=year)

    def get_ids(self, year):
        ids = None
        path = os.path.join(self.ids_path, '{}.csv'.format(year))
        with open(path, 'r') as file:
            reader = csv.reader(file)
            ids = [row[0] for row in reader]
        return ids

    def get_messages(self, id, year=None, clean=False):
        year = self.get_year(id) if year is None else year
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
        year = self.get_year(id) if year is None else year
        review = self.get_review(id, year)
        return review['description']

    def get_review(self, id, year=None):
        year = self.get_year(id) if year is None else year
        directory = self.get_reviews_path(year)
        for path in self._get_files(directory, pattern='reviews.*.json'):
            reviews = helpers.load_json(path)
            for review in reviews:
                if id == review['issue']:
                    return review
        raise Exception('No code review identified by {}'.format(id))

    def get_reviews(self, year):
        reviews = None
        directory = self.get_reviews_path(year)
        for path in self._get_files(directory, pattern='reviews.*.json'):
            if reviews is None:
                reviews = list()
            reviews += helpers.load_json(path)
        return reviews

    def get_reviews_path(self, year):
        return self.reviews_path.format(year=year)

    def get_year(self, id):
        for path in glob.glob(os.path.join(self.ids_path, '*.csv')):
            ids = None
            with open(path, 'r') as file:
                reader = csv.reader(file)
                ids = [int(row[0]) for row in reader]
            if ids is not None and id in ids:
                return os.path.basename(path).replace('.csv', '')
        raise Exception('No code review identified by {}'.format(id))

    def save_ids(self, year, ids):
        path = os.path.join(self.ids_path, '{}.csv'.format(year))
        with open(path, 'a') as file:
            writer = csv.writer(file)
            writer.writerows([(id,) for id in ids])
        return path

    def stat_review(self, id):
        stats = dict()
        review = self.get_review(id)
        stats['status'] = 'Closed' if review['closed'] else 'Open'
        stats['created'] = review['created']
        stats['reviewers'] = len(review['reviewers'])
        stats['messages'] = len(review['messages'])
        stats['patchsets'] = len(review['patchsets'])
        return stats

    def save_reviews(self, year, chunk, reviews, errors=None):
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

    def stat_reviews(self, year):
        stats = dict()
        reviews = self.get_reviews(year)
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
        stats['messages'] = helpers.sort(messages)
        stats['comments'] = helpers.sort(comments)
        stats['patchsets'] = helpers.sort(patchsets)
        return stats

    # Private Members

    def _get_files(self, path, pattern):
        files = [
                os.path.join(path, file)
                for file in glob.glob(os.path.join(path, pattern))
            ]
        return files

    def _parse(self, commit):
        pass

    # TODO: Remove function once bug information is available in JSON format
    def _to_dict(self, row):
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
