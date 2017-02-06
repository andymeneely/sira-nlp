"""
@AUTHOR: meyersbs
"""

from datetime import datetime as dt
from nltk.stem import WordNetLemmatizer
from nltk.tag import pos_tag
from nltk.corpus import wordnet, words

from app.lib.helpers import *
from app.lib.logger import *
from app.lib import helpers as h

VERBS = h.loadVerbs()

class Lemmatizer(object):
    """ Interface. """
    def __init__(self, tokens):
        """ Constructor. """
        self.tokens = tokens

    def execute(self):
        """ Raises NotImplementedError. """
        raise NotImplementedError("Lemmatizer is an abstract class. In must "
                                  "be implemented by another class. Try using "
                                  "the NLTKLemmatizer.")


def getPOS(token):
    return convertToWordNet(pos_tag([token])[0][1])

def convertToWordNet(tag):
    """
    NLTK's WordNetLemmatizer only accepts WordNet tags, but NLTK's pos_tag()
    returns Penn Treebank tags. The function maps the specified Treebank tag
    to its associated WordNet tag.
    """
    if tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN

def fixErrors(token, lemma, nextToken=None, prevToken=None):
    """
    Attempts to fix lemmatization errors with hardcoded rules.
    """
    global VERBS

    if token.lower() == "ca":
        if nextToken != None and nextToken.lower() == "n't":
            return "can"
    elif token.lower() == "left":
        if prevToken != None and getPOS(prevToken.lower()) == wordnet.VERB:
            return "leave"
    elif token == "'m":
        return "am"
    elif token == "'ll":
        return "will"
    elif token == "n't":
        return "not"
    elif token == "'ve":
        return "have"
    elif token == "'re":
        return "are"
    else:
        for verbList in VERBS:
            if lemma in verbList or token in verbList:
                return verbList[0]

    return lemma.lower()


class NLTKLemmatizer(Lemmatizer):
    """ Implements Lemmatizer. """
    def __init__(self, tokens):
        """ Constructor. """
        super().__init__(tokens)

    def execute(self):
        """ Return a list of all tokens within the specified string. """
        #start = dt.now()
        parser = WordNetLemmatizer()
        #info('NLTKLemmatizer completed in: {:.2f} mins'.format(get_elapsed(start, dt.now())))
        lemmas = []
        for i, token in enumerate(self.tokens):
            tempLemma = parser.lemmatize(token, getPOS(token))
            if i == len(self.tokens)-1 and len(self.tokens) == 1:
                tempLemma = fixErrors(token, tempLemma, None, None)
            elif i == len(self.tokens)-1 and len(self.tokens) >= 2:
                tempLemma = fixErrors(token, tempLemma, None, self.tokens[i-1])
            elif i == 0:
                tempLemma = fixErrors(token, tempLemma, self.tokens[i+1], None)
            else:
                tempLemma = fixErrors(token, tempLemma, self.tokens[i+1], self.tokens[i-1])
            lemmas.append(tempLemma)
        return lemmas
