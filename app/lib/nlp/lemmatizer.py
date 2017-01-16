import nltk

from app.lib.nlp import tokenizer


class Lemmatizer(object):
    def __init__(self, text):
        self.lemmatizer = nltk.WordNetLemmatizer()
        self.text = text

    def execute(self):
        return [
                self.lemmatizer.lemmatize(token)
                for token in tokenizer.Tokenizer(self.text).execute()
            ]
