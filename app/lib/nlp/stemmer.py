import nltk

from app.lib.nlp import tokenizer


class Stemmer(object):
    def __init__(self, text):
        self.stemmer = nltk.PorterStemmer()
        self.text = text

    def execute(self):
        return [
                self.stemmer.stem(token)
                for token in tokenizer.Tokenizer(self.text).execute()
            ]
