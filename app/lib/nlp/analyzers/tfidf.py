"""
@AUTHOR: nuthanmunaiah
"""

import math
import os
import pickle

import nltk

from app.lib.utils import parallel
from app.lib.nlp import preprocessor, tokenizer

CACHE_FILE = 'docfreq.pickle'


def do(iqueue, cqueue):
    document = iqueue.get(block=True)
    cqueue.put(set(preprocessor.Preprocessor(document).execute()), block=True)


def aggregate(oqueue, cqueue):
    idf = dict()
    count = 0

    while True:
        document = cqueue.get(block=True)
        if document == parallel.END:
            break

        count += 1
        for token in document:
            idf[token] = idf[token] + 1 if token in idf else 1

    for (token, freq) in idf.items():
        idf[token] = math.log(count / freq)

    oqueue.put(idf, block=True)


class TfIdf(object):
    """

    """
    def __init__(self, settings, num_documents):
        """
        Constructor.
        """
        self.cache_path = os.path.join(settings.NLP_CACHE_PATH, CACHE_FILE)
        self.cpu_count = settings.CPU_COUNT
        self.num_documents = num_documents
        self._documents = parallel.manager.Queue(settings.QUEUE_SIZE)

        self._idf = None

    def initialize(self):
        """

        """
        if self.is_cached:
            self._unpickle()
        else:
            self._build_idf()

    def get(self, document, token=None):
        """
        Returns the tf-idf value for the specified document and token.
        """
        if token:
            return self.get_tf(document, token) * self.get_idf(token)
        return {
                    t: tf * self.get_idf(t)
                    for (t, tf) in self.get_tf(document).items()
               }

    def get_idf(self, token=None):
        """
        Returns the idf value for the specified token.
        """
        if self._idf is None:
            raise Exception('initialize() must be invoked before get_idf().')

        if token:
            token = token.lower()
            return self._idf[token] if token in self._idf else 0.0
        return self._idf

    def get_tf(self, document, token=None):
        """
        Returns the tf value for the specified document and token.
        """
        tokens = tokenizer.Tokenizer(document).execute()
        if token:
            return tokens.count(token) / float(len(tokens))
        return {
                    token: freq / float(len(tokens))
                    for (token, freq) in nltk.FreqDist(tokens).items()
               }

    @property
    def documents(self):
        return self._documents

    @property
    def is_cached(self):
        return os.path.exists(self.cache_path)

    def _build_idf(self):
        self._idf = parallel.run(
                do, aggregate,
                self._documents, self.num_documents, self.cpu_count
            )
        self._pickle()

    def _pickle(self):
        with open(self.cache_path, 'wb') as file:
            pickle.dump(self._idf, file)

    def _unpickle(self):
        with open(self.cache_path, 'rb') as file:
            self._idf = pickle.load(file)
