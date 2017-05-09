from nltk.chunk import ChunkParserI, tree2conlltags as to_tags
from nltk.corpus import treebank_chunk, conll2000
from nltk.tag import UnigramTagger, BigramTagger


def tag_chunks(chunk_sents):
    tag_sents = [to_tags(tree) for tree in chunk_sents]
    return [[(t, c) for (w, t, c) in chunk_tags] for chunk_tags in tag_sents]


class ChunkTagger(ChunkParserI):
    def __init__(self):
        self._chunks = tag_chunks(treebank_chunk.chunked_sents())
        self._chunks += tag_chunks(conll2000.chunked_sents())
        self._backoff = UnigramTagger(self._chunks)
        self._chunk_tagger = BigramTagger(self._chunks, backoff=self._backoff)

    def parse(self, tokens):
        (tokens, tags) = zip(*tokens)
        chunks = self._chunk_tagger.tag(tags)
        return [(token, chunk[1]) for (token, chunk) in zip(tokens, chunks)]
