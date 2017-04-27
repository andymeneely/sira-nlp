from app.lib.nlp import counter, lemmatizer, postagger, tokenizer


class Summarizer(object):
    def __init__(self, text):
        self.text = text

    def execute(self):
        tokens = tokenizer.NLTKTokenizer(self.text).execute()
        lemmas = lemmatizer.NLTKLemmatizer(tokens).execute()
        pos = postagger.PosTagger(tokens).execute()

        summary = [
                (index + 1, t, l, p[1])
                for (index, (t, l, p)) in enumerate(zip(tokens, lemmas, pos))
            ]

        return summary
