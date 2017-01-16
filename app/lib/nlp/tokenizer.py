from nltk.tokenize import word_tokenize


class Tokenizer(object):
    def __init__(self, text):
        self.text = text

    def execute(self):
        return word_tokenize(self.text)
