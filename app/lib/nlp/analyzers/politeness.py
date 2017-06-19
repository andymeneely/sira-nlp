import json
import re
import sys
import subprocess
import traceback

from json import JSONDecodeError

from app.lib.nlp import analyzers

from politeness.classifier import Classifier
from politeness.helpers import set_corenlp_url

DEFAULT_POLITENESS = {'polite': '0', 'impolite': '0'}

class PolitenessAnalyzer(analyzers.Analyzer):
    def __init__(self, text, depparses, url="http://artifacts.gccis.rit.edu:41194/"):
        super(PolitenessAnalyzer, self).__init__(text)
        self.depparses = depparses
        self.classifier = Classifier()
        self.url = url
        set_corenlp_url(self.url)

    def analyze(self):
        politeness = DEFAULT_POLITENESS.copy()
        if self.text.strip() == '':
            return {'polite': 'EmptyText', 'impolite': 'EmptyText'}

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
            politeness = {'polite': str(extype), 'impolite': str(extype)}

        return politeness
