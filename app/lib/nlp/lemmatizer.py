"""
@AUTHOR: meyersbs
"""

from app.lib.nlp import preprocessor


class Lemmatizer(object):
    """
    Given a string of text, return a list of all of the lemmas for each token
    in the text.
    """
    def __init__(self, text):
        """
        Constructor.
        """
        self.text = text

    def execute(self):
        """
        Given a string of text, return a list of all of the lemmas for each
        token.
        """
        lemmas = preprocessor.Preprocessor(self.text).execute()
        return lemmas[1]
