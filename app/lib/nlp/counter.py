"""
@AUTHOR: nuthanmunaiah
"""

import nltk


class Counter(object):

    def __init__(self, tokens):
        """ Constructor. """
        self.freqdist = nltk.FreqDist(tokens)

    def execute(self):
        """ Returns a dictionary of tokens and their frequencies. """
        return dict(self.freqdist)
