"""
@AUTHOR: meyersbs
"""

from spacy.en import English

class Preprocessor(object):
    """
    Preforms a variety of preprocessing tasks.
    """
    def __init__(self, text):
        """
        Constructor.
        """
        self.parser = English()
        self.text = text

    def execute(self):
        """
        Tokenize, lemmatize, and remove stop-words from the text. Return a list
        of the remaining tokens lowercased.
        """
        parsedText = self.parser(self.text)
        tokens = []
        lemmas = []
        for i, token in enumerate(parsedText):
            tokens.append(token.orth_)
            lemmas.append(token.lemma_)

        return tokens, lemmas
