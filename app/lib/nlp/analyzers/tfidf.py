import math
import os
import pickle

import nltk

from app.lib.nlp import preprocessor, tokenizer

CACHE_FILE = 'docfreq.pickle'


class TfIdf(object):
    def __init__(self, settings, documents):
        self.cache_path = os.path.join(settings.NLP_CACHE_PATH, CACHE_FILE)
        self.documents = documents
        self._idf = None

    def initialize(self):
        if self.is_cached:
            self._unpickle()
        else:
            self._build_idf()

    def get(self, document, token=None):
        if token:
            return self.get_tf(document, token) * self.get_idf(token)
        return {
                    t: tf * self.get_idf(t)
                    for (t, tf) in self.get_tf(document).items()
               }

    def get_idf(self, token=None):
        if self._idf is None:
            raise Exception('initialize() must be invoked before get_idf().')

        if token:
            token = token.lower()
            return self._idf[token] if token in self._idf else 0.0
        return self._idf

    def get_tf(self, document, token=None):
        tokens = tokenizer.Tokenizer(document).execute()
        if token:
            return tokens.count(token) / float(len(tokens))
        return {
                    token: freq / float(len(tokens))
                    for (token, freq) in nltk.FreqDist(tokens).items()
               }

    @property
    def is_cached(self):
        return os.path.exists(self.cache_path)

    def _build_idf(self):
        self._idf = dict()

        count = 0.0
        for document in self.documents:
            count += 1
            for token in set(preprocessor.Preprocessor(document).execute()):
                self._idf[token] = self._idf[token] + 1 \
                                   if token in self._idf else 1

        for (token, freq) in self._idf.items():
            self._idf[token] = math.log(count / freq)

        self._pickle()

    def _pickle(self):
        with open(self.cache_path, 'wb') as file:
            pickle.dump(self._idf, file)

    def _unpickle(self):
        with open(self.cache_path, 'rb') as file:
            self._idf = pickle.load(file)
