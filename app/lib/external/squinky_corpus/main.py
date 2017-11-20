import csv
import itertools
import numpy as np
import re
import sys
import _pickle

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from nltk import word_tokenize, pos_tag, sent_tokenize
from nltk.chunk import ChunkParserI, tree2conlltags as to_tags
from nltk.corpus import conll2000, treebank_chunk, wordnet
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from nltk.tag import UnigramTagger, BigramTagger
from scipy.sparse import csr_matrix
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

LEMMATIZER = WordNetLemmatizer()
STEMMER = PorterStemmer()
WORDNET_POS = {
    'N': wordnet.NOUN, 'V': wordnet.VERB, 'J': wordnet.ADJ, 'R': wordnet.ADV
}
GREEK_LOWER = re.compile(u'[αβγδεζηθικλμξπρσςτυφψω]')
GREEK_UPPER = re.compile(u'[ΓΔΘΛΞΠΣΦΨΩ]')
ENGLISH_LOWER = re.compile(r'[a-z]')
ENGLISH_UPPER = re.compile(r'[A-Z]')
DIGIT = re.compile(r'[0-9]')
ROMAN_LOWER = re.compile(
        'm{0,4}(cm|cd|d?c{0,3})(xc|xl|l?x{0,3})(ix|iv|v?i{0,3})'
    )
ROMAN_UPPER = re.compile(
        'M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})'
    )

def tag_chunks(chunk_sents):
    tag_sents = [to_tags(tree) for tree in chunk_sents]
    return [[(t, c) for (w, t, c) in chunk_tags] for chunk_tags in tag_sents]


CHUNKS = tag_chunks(treebank_chunk.chunked_sents()) + \
         tag_chunks(conll2000.chunked_sents())
TAGGER = BigramTagger(CHUNKS, backoff=UnigramTagger(CHUNKS))


class ChunkTagger(ChunkParserI):
    def parse(self, tokens):
        (tokens, tags) = zip(*tokens)
        chunks = TAGGER.tag(tags)
        return [(token, chunk[1]) for (token, chunk) in zip(tokens, chunks)]

CHUNKER = ChunkTagger()

def get_wordpattern(word):
    pattern = ''.join(get_charpattern(character) for character in word)
    return ''.join(c for c, _ in itertools.groupby(pattern))


def get_charpattern(character):
    if not character.isalnum():
        return '!'
    elif ENGLISH_UPPER.search(character):
        return 'A'
    elif ENGLISH_LOWER.search(character):
        return 'a'
    elif DIGIT.search(character):
        return '0'
    elif GREEK_UPPER.search(character):
        return 'G'
    elif GREEK_LOWER.search(character):
        return 'g'
    elif ROMAN_UPPER.search(character):
        return 'R'
    elif ROMAN_LOWER.search(character):
        return 'r'

def _pos_to_wordnet(pos):
    return WORDNET_POS.get(pos[0], wordnet.NOUN)

class Word(object):
    def __init__(self, word, pos, position, label, prev, next, chunk):
        self.word = word
        self.pos = pos
        self.position = position
        self.label = label
        self.prev = prev
        self.next = next
        self.chunk = chunk
        self.pattern = get_wordpattern(self.word)
        self.prefixes = ['prefix_{}_{}'.format(i, self.word[:i]) for i in [3, 4, 5]]
        self.suffixes = ['suffix_{}_{}'.format(i, self.word[-i:]) for i in [3, 4, 5]]
        self.lemma = LEMMATIZER.lemmatize(self.word, pos=_pos_to_wordnet(self.pos))
        self.stem = STEMMER.stem(self.word)

    def get_word(self):
        return self.word

    def get_pos(self):
        return self.pos

    def get_position(self):
        return self.position

    def get_label(self):
        return self.label

    def get_features(self):
        feats = {
                "IND_" + str(self.position):1.0,
                "POS_" + str(self.pos):1.0,
                "LEM_" + str(self.lemma):1.0,
                "STM_" + str(self.stem):1.0,
                "PAT_" + str(self.pattern):1.0,
                "CUR_" + str(self.word):1.0,
                "CNK_" + str(self.chunk):1.0,
            }
        if self.prev is not None:
            feats.update({"PRV_" + str(self.prev):1.0})
        if self.next is not None:
            feats.update({"NXT_" + str(self.next):1.0})
        for p in self.prefixes:
            feats.update({"PRE_" + str(p):1.0})
        for s in self.suffixes:
            feats.update({"SUF_" + str(s):1.0})

        return feats


class Sentence(object):
    def __init__(self, sentence, label, pos_label="P", neg_label="N"):
        self.sentence = sentence
        self.label = pos_label if label <= 4.00 else neg_label
        self.words = list()

        tokens = word_tokenize(self.sentence)
        pos_tags = pos_tag(tokens)
        chunks = CHUNKER.parse(pos_tags)

        for i, token in enumerate(pos_tags):
            prev_word = pos_tags[i-1][0] if i-1 >= 0 else None
            next_word = pos_tags[i+1][0] if i+1 < len(pos_tags) else None
            w = Word(token[0], token[1], i, self.label, prev_word, next_word, chunks[i])
            self.words.append(w)

    def _score(self):
        feats = dict()
        for w in self.words:
            feats.update(w.get_features())
        with open('vec_form.p', 'rb') as V:
            VEC = _pickle.load(V)
            with open('cls_form.p', 'rb') as C:
                CLS = _pickle.load(C)
                fv = VEC.transform(feats)
                probs = CLS.predict_proba(fv)
                print("  FORMAL: " + str(probs[0][1]))
                print("INFORMAL: " + str(probs[0][0]))
        with open('vec_info.p', 'rb') as V:
            VEC = _pickle.load(V)
            with open('cls_info.p', 'rb') as C:
                CLS = _pickle.load(C)
                fv = VEC.transform(feats)
                probs = CLS.predict_proba(fv)
                print("  INFORMATIVE: " + str(probs[0][1]))
                print("UNINFORMATIVE: " + str(probs[0][0]))
        with open('vec_impl.p', 'rb') as V:
            VEC = _pickle.load(V)
            with open('cls_impl.p', 'rb') as C:
                CLS = _pickle.load(C)
                fv = VEC.transform(feats)
                probs = CLS.predict_proba(fv)
                print("  IMPLICATIVE: " + str(probs[0][1]))
                print("UNIMPLICATIVE: " + str(probs[0][0]))

    def get_sentence(self):
        return self.sentence

    def get_label(self):
        return self.label

    def get_words(self):
        return self.words

    def get_features(self):
        feats = dict()
        for word in self.words:
            feats.update(word.get_features())

        return feats

def classify():
    with open("mturk_merged.csv", newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')

        next(csv_reader, None) # Skip header row

        labs = {1: ["F", "I"], 2: ["I", "U"], 3: ["I", "U"]}
        sents = dict()
        for sentence in csv_reader:
            # sentence[0]: id, sentence[1]: formality, sentence[2]: informativeness,
            # sentence[3]: implicature, sentence[5]: sentence
            sent = Sentence(sentence[-1], float(sentence[3]), labs[3][0], labs[3][1])
            sents[int(sentence[0])] = sent
        print("#  SENTENCES: {:d}".format(len(sents.keys())))

        print("Gathering Features...")
        X, y = list(), list()
        for key, sent in sents.items():
            X.append(sent.get_features())
            y.append(sent.get_label())

        print("Splitting Train/Test...")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.0)

        print("Generating Feature Vectors...")
        vectorizer = DictVectorizer()
        X_train = vectorizer.fit_transform(X_train)

        print("Dumping Vectorizer to Disk...")
    #    with open('vec_form.p', 'wb') as f:
    #    with open('vec_info.p', 'wb') as f:
        with open('vec_impl.p', 'wb') as f:
            _pickle.dump(vectorizer, f)

        print("Training Classifier...")
        classifier = LogisticRegression()
        classifier.fit(X_train, y_train)

        print("Dumping Classifier to Disk...")
    #    with open('cls_form.p', 'wb') as f:
    #    with open('cls_info.p', 'wb') as f:
        with open('cls_impl.p', 'wb') as f:
            _pickle.dump(classifier, f)

        '''
        print("Making Predictions...")
        X_test = vectorizer.transform(X_test)
        y_pred = classifier.predict(X_test)

        print(classification_report(y_test, y_pred))
        print("\n")
        print(confusion_matrix(y_test, y_pred))
        '''

def score(sentences):
    with open(sentences, newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for sentence in csv_reader:
            print("SENT: " + sentence[4][:50])
            print("FORM: " + str(sentence[1]))
            print("INFO: " + str(sentence[2]))
            print("IMPL: " + str(sentence[3]))

            sent = Sentence(sentence[4], 0.00)
            sent._score()

if __name__ == "__main__":
    args = sys.argv[1:]
    if args[0] == 'score':
        score(args[1])
    elif args[0] == 'classify':
        #classify()
        pass

