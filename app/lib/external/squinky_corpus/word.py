import itertools
import re

from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer

LEMMATIZER = WordNetLemmatizer()
WORDNET_POS = {
    'N': wordnet.NOUN, 'V': wordnet.VERB, 'J': wordnet.ADJ, 'R': wordnet.ADV
}
STEMMER = PorterStemmer()

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


class _Word(object):
    def __init__(self, word, pos, position, prev, next, chunk):
        self.word = word
        self.pos = pos
        self.position = position
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

