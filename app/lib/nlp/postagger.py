import nltk

from app.lib.nlp import tokenizer


class PosTagger(object):
    def __init__(self, text):
        self.text = text

    def execute(self):
        return nltk.pos_tag(tokenizer.Tokenizer(self.text).execute())
