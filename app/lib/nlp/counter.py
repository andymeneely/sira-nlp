import nltk


class Counter(object):
    def __init__(self, tokens):
        self.freqdist = nltk.FreqDist(tokens)

    def execute(self):
        return dict(self.freqdist)
