import string

from nltk.corpus import stopwords

FILTERS = {
        'SW': set(stopwords.words('english')),
        'PU': set(tuple(string.punctuation))
    }


class TokenRemover(object):
    def __init__(self, tokens, filters=['SW', 'PU']):
        self.tokens = tokens
        self.filters = set()
        for filter in filters:
            if filter not in list(FILTERS.keys()):
                raise Exception('{} is an unknown filter'.format(filter))
            self.filters |= FILTERS[filter]

    def execute(self):
        return [
                token
                for token in self.tokens if token.lower() not in self.filters
            ]
