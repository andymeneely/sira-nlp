from app.lib.nlp import lemmatizer, tokenizer, tokenremover


class Preprocessor(object):
    def __init__(self, text):
        self.text = text

    def execute(self):
        tokens = tokenizer.Tokenizer(self.text).execute()
        tokens = lemmatizer.Lemmatizer(tokens).execute()
        tokens = tokenremover.TokenRemover(tokens).execute()
        return [token.lower() for token in tokens]
