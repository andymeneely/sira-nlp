import json
import os
import random
import re
import sys
import subprocess
import traceback

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from json import JSONDecodeError

from app.lib.nlp import analyzers

from uncertainty.classifier import Classifier

classifier = Classifier(granularity='word', binary=False)


class UncertaintyAnalyzer(analyzers.Analyzer):
    def __init__(self, tokens, root_type='stem'):
        super(UncertaintyAnalyzer, self).__init__("")
        self.tokens = tokens
        self.root = root_type

    def analyze(self):
        try:
            tok_list = []
            if self.root == "stem":
                for tok in self.tokens:
                    tok_list.append((tok.token, tok.stem, tok.pos, tok.chunk))
            else:
                for tok in self.tokens:
                    tok_list.append((tok.token, tok.lemma, tok.pos, tok.chunk))

            uncertainty = classifier.predict(tok_list)
        except Exception as error:  # pragma: no cover
            sys.stderr.write('Exception\n')
            sys.stderr.write('  Text: {}\n'.format(self.text[:50]))
            extype, exvalue, extrace = sys.exc_info()
            traceback.print_exception(extype, exvalue, extrace)
            uncertainty = {"ERROR": str(extype)}

        return uncertainty
