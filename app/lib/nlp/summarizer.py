from app.lib.nlp import counter, lemmatizer, postagger, tokenizer


class Summarizer(object):
    def __init__(self, text):
        self.text = text

    def execute(self):
        tokens = tokenizer.NLTKTokenizer(self.text).execute()

        lemmas = lemmatizer.NLTKLemmatizer(tokens).execute()
        pos = postagger.PosTagger(tokens).execute()
        frequency = counter.Counter(pos).execute()

        summary = [
                (t, l, frequency[p], p[1])
                for (t, l, p) in zip(tokens, lemmas, pos)
            ]

        return list(set(summary))
