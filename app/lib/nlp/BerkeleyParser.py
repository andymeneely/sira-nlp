"""
@AUTHOR: meyersbs
"""

import os
import pexpect
import re

from app import BERKELEY_JAR_PATH as JAR_PATH
from app import BERKELEY_GRAMMAR_PATH as GRMR_PATH
from app.lib import logger


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

        self.pattern = '\r\n.*\r\n'
        self.parse('')

    def parse(self, text):
        """
        Given a sentence or a list of sentences, return the syntactic parse,
        or 'treestring' of each sentence. For example:
            INPUT:  I am the walrus.
            OUTPUT: '( (S (NP (PRP I)) (VP (VBP am) (NP (DT the) (NN walrus.)))) )'
        """
        if type(text) == list:
            output = []
            for sent in text:
                if type(sent) != str:
                    pass
                else:
                    self.parser.sendline(self.__escape(sent))
                    self.parser.expect(self.pattern)
                    temp = self.__clean(self.parser.after)
                    if type(temp) == str and temp != '':
                        output.append(temp)
                    else:
                        for t in temp:
                            if t != '':
                                output.append(t)

            return output
        elif type(text) == str:
            output = []
            self.parser.sendline(self.__escape(text))
            self.parser.expect(self.pattern)

            temp = self.__clean(self.parser.after)
            if type(temp) == str and temp != '':
                output.append(temp)
            else:
                output.append('')

            return output
        else:
            raise ValueError('Input to the BerkeleyParser must be of type '
                             'list or str, not %s' % (str(type(text))))

    def deactivate(self, lg=logger):
        """
        Since the Berkeley Parser is Java and heavy on system resources, we
        have to remember to kill it when we're done using it.
        """
        lg.warning('Deactivating the Berkeley Parser...')
        self.parser.terminate()

    def __clean(self, bytestring):
        """
        The output of the Berkeley Parser is a byte encoded string, so we need
        to decode it and strip the special sequence '\r\n' in order to get a
        proper treestring.
        """
        treestring = bytestring.decode("utf-8")
        treestring = re.sub(r'\r\n', '', treestring)

        return treestring.split('\n')

    def __escape(self, text):
        """
        The Yngve and Frazier algorithms parse treestrings for matching
        parentheses, so in order to ensure they don't fail, the treestrings
        need to have parentheses 'escaped'.
        """
        text = re.sub(r'\(', '[', text)
        text = re.sub(r'\)', ']', text)

        return text


