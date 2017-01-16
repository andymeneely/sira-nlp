from nltk.corpus import stopwords

STOPWORDS = stopwords.words('english')


class StopWordsRemover(object):
    def __init__(self, tokens):
        self.tokens = tokens

    def execute(self):
        return [token for token in self.tokens if token not in STOPWORDS]
