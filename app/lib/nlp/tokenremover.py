"""
@AUTHOR: nuthanmunaiah
"""

import string

from nltk.corpus import stopwords

FILTERS = {
        'SW': set(stopwords.words('english')),
        'PU': set(tuple(string.punctuation))
    }


class TokenRemover(object):
    """
    Given a list of tokens and a list of filters, return a list of tokens
    excluding the filtered words.
    """
    def __init__(self, tokens, filters=['SW', 'PU']):
        """
        Constructor.
        """
        self.tokens = tokens
        self.filters = set()
        for filter in filters:
            if filter not in list(FILTERS.keys()):
                raise Exception('{} is an unknown filter'.format(filter))
            self.filters |= FILTERS[filter]

    def execute(self):
        """
        For each token in the given list, if the token is not in the specified
        filter(s), append it to a new list. Return the new list.
        """
        return [
                token
                for token in self.tokens if token.lower() not in self.filters
            ]
