import nltk


class PosTagger(object):
    def __init__(self, tokens):
        self.tokens = tokens

    def execute(self):
        return nltk.pos_tag(self.tokens)
