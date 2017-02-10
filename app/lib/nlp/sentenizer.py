"""
@AUTHOR: meyersbs
"""

from nltk.tokenize import sent_tokenize

class Sentenizer(object):
    """ Interface. """
    def __init__(self, text):
        """ Constructor. """
        self.text = text

    def execute(self):
        """ Raises NotImplementedError. """
        raise NotImplementedError("Sentenizer is an abstract class. In must be "
                                  "implemented by another class. Try using "
                                  "the NLTKSentenizer.")


class NLTKSentenizer(Sentenizer):
    """ ImplementsSentenizer. """
    def __init__(self, text):
        """ Constructor. """
        super(NLTKSentenizer, self).__init__(text)

    def execute(self):
        """ Return a list of all sentences within the specified string. """
        tempSents = self.text.strip().split('\n')
        sents = []
        for s in tempSents:
            sents += sent_tokenize(s.strip())

        return sents

