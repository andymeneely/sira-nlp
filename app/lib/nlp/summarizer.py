from app.lib.nlp import chunktagger, counter, lemmatizer, postagger, stemmer, \
                        tokenizer


class Summarizer(object):
    def __init__(self, text):
        self.text = text

    def execute(self):
        tokens = tokenizer.NLTKTokenizer(self.text).execute()
        lemmas = lemmatizer.NLTKLemmatizer(tokens).execute()
        stems = stemmer.Stemmer(tokens).execute()
        pos = postagger.PosTagger(tokens).execute()
        chunk = chunktagger.ChunkTagger().parse(pos)

        summary = zip(tokens, stems, lemmas, pos, chunk)
        summary = [
                (index + 1, t, s, l, p[1], c[1])
                for (index, (t, s, l, p, c)) in enumerate(summary)
            ]

        return summary
