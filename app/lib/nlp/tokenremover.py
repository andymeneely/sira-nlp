"""
@AUTHOR: nuthanmunaiah
"""

import re
import string

from nltk.corpus import stopwords

FILTERS = {
        'SW': set(stopwords.words('english')),
        'PU': set(tuple(string.punctuation)),
        'NU': '^[-+]?(\d+\.?\d+|\.?\d+|\d+\.?)$',
        'WL': '^.{{{length},}}$',
        'SC': '\W'
    }
CONFIGURATION = {
        # 12 is the maximum of the word lengths that captures 99% of the words
        # in the Brown, Gutenberg and Reuters data sets. By default, token
        # remover will remove all words that are longer than 12 characters.
        'WL': {'length': 13}
    }


class TokenRemover(object):
    """
    Given a list of tokens and a list of filters, return a list of tokens
    excluding the filtered words.
    """
    def __init__(self, tokens, filters=None, configuration=None):
        """ Constructor. """
        self.tokens = tokens
        filters = list(FILTERS.keys()) if filters is None else filters
        configuration = (
                CONFIGURATION if configuration is None else configuration
            )
        self.re_filter = None
        self.set_filter = set()

        re_filters = list()
        for filter in filters:
            if filter not in list(FILTERS.keys()):
                raise Exception('{} is an unknown filter'.format(filter))
            if isinstance(FILTERS[filter], set):
                self.set_filter |= FILTERS[filter]
            else:
                re_filters.append(
                        FILTERS[filter].format(**configuration[filter])
                        if filter in configuration
                        else FILTERS[filter]
                    )

        if len(re_filters) > 0:
            self.re_filter = re.compile(
                    '({})'.format('|'.join(re_filters)), flags=re.ASCII
                )

    def execute(self):
        """
        For each token in the given list, if the token is not in the specified
        filter(s), append it to a new list. Return the new list.
        """
        tokens = self.tokens
        if self.re_filter is not None:
            tokens = [
                    token for token in tokens
                    if not self.re_filter.search(token.lower())
                ]
        tokens = [
                token for token in tokens
                if token.lower() not in self.set_filter
            ]
        return tokens
