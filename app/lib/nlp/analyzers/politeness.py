import json
import re
import sys
import subprocess
import traceback

from json import JSONDecodeError

from app.lib.nlp import analyzers

from app.lib.external.politeness.model import *

DEFAULT_POLITENESS = {'polite': '0', 'impolite': '0'}

class PolitenessAnalyzer(analyzers.Analyzer):
    def __init__(self, text, depparses):
        super(PolitenessAnalyzer, self).__init__(text)
        self.depparses = depparses

    def analyze(self):
        politeness = DEFAULT_POLITENESS.copy()
        if self.text.strip() == '':
            return {'polite': 'EmptyText', 'impolite': 'EmptyText'}

        try:
            data = {'sentences': [self.text], 'parses': [self.depparses]}
            politeness = score(data)
        except Exception as error: # pragma: no cover
            sys.stderr.write('Exception\n')
            sys.stderr.write('  Text: {}\n'.format(self.text[:50]))
            extype, exvalue, extrace = sys.exc_info()
            traceback.print_exception(extype, exvalue, extrace)
            politeness = {'polite': str(extype), 'impolite': str(extype)}

        return politeness
