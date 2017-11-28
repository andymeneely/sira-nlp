import json
import re
import sys
import subprocess
import traceback

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from json import JSONDecodeError

from app.lib.helpers import JSON_NULL
from app.lib.nlp import analyzers

from politeness.classifier import Classifier

DEFAULT_POLITENESS = {'polite': JSON_NULL, 'impolite': JSON_NULL}

class PolitenessCleanAnalyzer(analyzers.Analyzer):
    def __init__(self, text, depparses):
        super(PolitenessCleanAnalyzer, self).__init__(text)
        self.depparses = depparses
        self.classifier = Classifier()

    def analyze(self):
        politeness = DEFAULT_POLITENESS.copy()
        if self.text.strip() == '':
            return politeness

        try:
            data = {'sentence': self.text, 'parses': [self.depparses]}
            response = self.classifier.predict(data)[-1]['document']
            politeness['polite'] = response[0]
            politeness['impolite'] = response[1]
        except Exception as error: # pragma: no cover
            sys.stderr.write('Exception\n')
            sys.stderr.write('  Text: {}\n'.format(self.text[:50]))
            extype, exvalue, extrace = sys.exc_info()
            traceback.print_exception(extype, exvalue, extrace)

        return politeness
