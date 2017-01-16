from nltk.corpus import stopwords

from app.lib.nlp import tokenizer

STOPWORDS = stopwords.words('english')


class StopWordsRemover(object):
    def __init__(self, text):
        self.text = text

    def execute(self):
        return [
                token
                for token in tokenizer.Tokenizer(self.text).execute()
                if token not in STOPWORDS
            ]
