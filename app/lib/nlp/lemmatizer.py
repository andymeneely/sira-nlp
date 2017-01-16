import nltk


class Lemmatizer(object):
    def __init__(self, tokens):
        self.lemmatizer = nltk.WordNetLemmatizer()
        self.tokens = tokens

    def execute(self):
        return [self.lemmatizer.lemmatize(token) for token in self.tokens]
