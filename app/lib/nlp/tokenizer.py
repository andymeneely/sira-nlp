"""
@AUTHOR: meyersbs
"""

from app.lib.nlp import preprocessor


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
        tokens = preprocessor.Preprocessor(self.text).execute()
        return tokens[0]
