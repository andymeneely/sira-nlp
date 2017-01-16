import nltk


class Stemmer(object):
    def __init__(self, tokens):
        self.stemmer = nltk.PorterStemmer()
        self.tokens = tokens

    def execute(self):
        return [self.stemmer.stem(token) for token in self.tokens]
