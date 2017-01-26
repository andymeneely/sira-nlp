"""
@AUTHOR: nuthanmunaiah
"""

from nltk.tokenize import word_tokenize


class Tokenizer(object):
    """
    Given a string of text, return a list of all of the tokens within the text.
    """
    def __init__(self, text):
        """
        Constructor.
        """
        self.text = text

    def execute(self):
        """
        Given a string of text, return a list of all of the tokens within the
        text.
        """
        return word_tokenize(self.text)
