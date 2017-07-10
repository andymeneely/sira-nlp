"""
@AUTHOR: nuthanmunaiah
"""

import nltk


class Stemmer(object):
    """
    Given a list of tokens, return a list of corresponding stems.
    """
    def __init__(self, tokens):
        """ Constructor. """
        self.stemmer = nltk.PorterStemmer()
        self.tokens = tokens

    def execute(self):
        """
        Given a list of tokens, return a list of stems associated with those
        tokens.
        """
        #print(self.tokens)
        stems = []
        for token in self.tokens:
            #print("TOK: " + str(self.tokens))
            stems.append(self.stemmer.stem(token).lower())
            #print("STM: " + str(stems))
#        return [self.stemmer.stem(token).lower() for token in self.tokens]
        return stems
