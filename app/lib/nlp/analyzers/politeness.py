import json
import re
import sys
import subprocess
import traceback

from json import JSONDecodeError

from app.lib.nlp import analyzers

from app.lib.external.politeness.model import *

DEFAULT_POLITENESS = {'polite': 'X', 'impolite': 'X'}


class PolitenessAnalyzer(analyzers.Analyzer):
    def __init__(self, text, parses, sents):
        super(PolitenessAnalyzer, self).__init__(text)
        self.parses = parses
        self.sents = sents

    def analyze(self):
        politeness = DEFAULT_POLITENESS.copy()
        if self.text.strip() == '':
            return {'polite': 'EmptyText', 'impolite': 'EmptyText'}

        try:
            data = {'sentences': self.sents, 'parses': self.parses}
            politeness = subprocess.Popen(['/home/bsm9339/.venv2.7/bin/python',
                                           '/home/bsm9339/politeness/model.py', json.dumps(data)], stdout=subprocess.PIPE).communicate()[0]
#            print(politeness)
            politeness = json.loads(politeness.decode('utf-8').strip('\n'))
            print(politeness)
        except JSONDecodeError as error:
            sys.stderr.write('Exception\n')
            sys.stderr.write('  Text: {}\n'.format(self.text[:50]))
            extype, exvalue, extrace = sys.exc_info()
            traceback.print_exception(extype, exvalue, extrace)
            return politeness

        return politeness
