"""
@AUTHOR: nuthanmunaiah
"""

import nltk


class Lemmatizer(object):
    """
    Given a list of tokens, return a list of the same length containing
    the lemma of each token.
    """
    def __init__(self, tokens):
        """
        Constructor.
        """
        self.lemmatizer = nltk.WordNetLemmatizer()
        self.tokens = tokens

    def execute(self):
        """
        Returns a list of lemmas corresponding to each token in the tokens list.
        """
        return [self.lemmatizer.lemmatize(token) for token in self.tokens]
