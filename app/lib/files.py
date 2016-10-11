import csv
import glob
import json
import os
import re

from app.lib.helpers import *

# Match the line of header that marks the beginning of quoted text.
# E.g., On 2008/01/01 00:00:01, Raymond Reddington wrote:
RESPONSE_HEAD_RE = re.compile(
        '^On \d{4}\/\d{1,2}\/\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}, .* wrote:$\n',
        flags=re.MULTILINE
    )
# Match lines of quoted text.
# E.g., > Happy New Year
QUOTED_TEXT_RE = re.compile(
        '^>.*$\n', flags=re.MULTILINE
    )
# Match code review diff location along with a line of contextual content.
# E.g., http://codereview.chromium.org/15076/diff/1/6
#       File chrome/browser/net/dns_master.cc (right):
CODEREVIEW_URL_RE = re.compile(
        '^https?:\/\/(codereview.chromium.org|chromiumcodereview.appspot.com)'
        '\/\d+\/diff\/.*\n.*\n', flags=re.MULTILINE
    )
# Subsequent new lines
NEWLINES_RE = re.compile('(^$\n)+', flags=re.MULTILINE)


class Files(object):
    def __init__(self, settings):
        self.ids_path = settings.IDS_PATH
        self.reviews_path = settings.REVIEWS_PATH
        self.bots = settings.BOTS

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
            text = self._clean(message['text']) if clean else message['text']
            messages.append((sender, text))
        return messages

    def get_description(self, id, year=None):
        year = self.get_year(id) if year is None else year
        review = self.get_review(id, year)
        return review['description']

    def get_review(self, id, year=None):
        year = self.get_year(id) if year is None else year
        directory = self.get_reviews_path(year)
        for path in self._get_files(directory):
            with open(path, 'r') as file:
                reviews = json.load(file)
                for review in reviews:
                    if id == review['issue']:
                        return review
        raise Exception('No code review identified by {}'.format(id))

    def get_reviews(self, year):
        reviews = None
        directory = self.get_reviews_path(year)
        for path in self._get_files(directory):
            with open(path, 'r') as file:
                if reviews is None:
                    reviews = list()
                reviews += json.load(file)
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
        stats['messages'] = sort(messages)
        stats['comments'] = sort(comments)
        stats['patchsets'] = sort(patchsets)
        return stats

    def _get_files(self, path):
        files = [
                os.path.join(path, file)
                for file in glob.glob(os.path.join(path, 'reviews.*.json'))
            ]
        return files

    def _clean(self, text):
        text = RESPONSE_HEAD_RE.sub('', text)
        text = QUOTED_TEXT_RE.sub('', text)
        text = CODEREVIEW_URL_RE.sub('', text)
        text = NEWLINES_RE.sub('\n', text)
        return text
