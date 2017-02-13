"""
@AUTHOR: meyersbs
"""

import os
import pexpect

JAR_PATH = os.path.join(os.path.dirname(__file__) + "/BerkeleyParser-1.7.jar")
GRMR_PATH = os.path.join(os.path.dirname(__file__) + "/eng_sm6.gr")

class BerkeleyParser(object):
    """
    This class instantiates a BerkeleyParser objects, which should make
    syntactic parsing a little faster by preventing the need to reload a grammar
    file for every call.

    This interface is based on: https://github.com/shiman/perkeleyparser
    """
    def __init__(self, num_threads=1):
        """ Constructor. """
        global JAR_PATH, GRMR_PATH
        self.parser = pexpect.spawn('java -jar %s -gr %s -nThreads %i' %
                                    (JAR_PATH, GRMR_PATH, num_threads))

        self.pattern('\r\n.*\r\n')
        self.parse('')

    def parse(self, text):
        """
        Given a sentence or a list of sentences, return the syntactic parse,
        or 'treestring' of each sentence. For example:
            INPUT:  I am the walrus.
            OUTPUT: '( (S (NP (PRP I)) (VP (VBP am) (NP (DT the) (NN walrus.)))) )'
        """
        if type(text) = list:
            output = []
            for sent in text:
                self.parser.sendline(sent)
                self.parser.expect(self.pattern)
                output.append(self.parser.after)

            return output
        elif type(text) = str:
            self.parser.sendline(sent)
            self.parser.expect(self.pattern)

            return self.parser.after
        else:
            raise InputError('Input to the BerkeleyParser must be of type '
                             'list or str.')

    def deactivate(self):
        """
        Since the Berkeley Parser is Java and heavy on system resources, we
        have to remember to kill it when we're done using it.
        """
        self.parser.terminate()
