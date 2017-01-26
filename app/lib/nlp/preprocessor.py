"""
@AUTHOR: nuthanmunaiah
"""

from app.lib.nlp import lemmatizer, tokenizer, tokenremover


class Preprocessor(object):
    """
    Preforms a variety of preprocessing tasks.
    """
    def __init__(self, text):
        """
        Constructor.
        """
        self.text = text

    def execute(self):
        """
        Tokenize, lemmatize, and remove stop-words from the text. Return a list
        of the remaining tokens lowercased.
        """
        tokens = tokenizer.Tokenizer(self.text).execute()
        tokens = lemmatizer.Lemmatizer(tokens).execute()
        tokens = tokenremover.TokenRemover(tokens).execute()
        return [token.lower() for token in tokens]
