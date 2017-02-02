from app.lib.nlp import counter, lemmatizer, postagger, tokenizer


class Summarizer(object):
    def __init__(self, text):
        self.text = text

    def execute(self):
        tokens = tokenizer.NLTKTokenizer(self.text).execute()

        lemma = lemmatizer.NLTKLemmatizer(tokens).execute()
        frequency = counter.Counter(tokens).execute()
        pos = postagger.PosTagger(tokens).execute()

        summary = [
                (tokens[i], lemma[i], frequency[tokens[i]], pos[i][1])
                for i in range(0, len(tokens))
            ]
        return summary
