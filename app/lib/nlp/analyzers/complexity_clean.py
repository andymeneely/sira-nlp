import sys
import traceback

from json import JSONDecodeError as JSONDE
from json.decoder import JSONDecodeError as DJSONDE

import requests

from requests.exceptions import RequestException

from app.lib.helpers import JSON_NULL
from app.lib.nlp import analyzers
from app.management.commands import complexity as comp

DEFAULT_COMPLEXITY = {'yngve': JSON_NULL, 'frazier': JSON_NULL,
                      'pdensity': JSON_NULL, 'cdensity': JSON_NULL}

'''
################################################################################
import signal

class timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message
    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)
    def __exit__(self, type, value, traceback):
        signal.alarm(0)
################################################################################
'''


class ComplexityCleanAnalyzer(analyzers.Analyzer):
    def __init__(self, text, treeparse):
        super(ComplexityCleanAnalyzer, self).__init__(text)
        self.treeparse = treeparse

    def analyze(self):
        complexity = DEFAULT_COMPLEXITY.copy()
        if self.text.strip() == '':
            pass

        try:
            if self.treeparse not in ["", 'null']:
                complexity = comp.get_syntactic_complexity(self.treeparse)
        except Exception as error: # pragma: no cover
            sys.stderr.write('Exception\n')
            sys.stderr.write('  Text: {}\n'.format(self.text[:50]))
            extype, exvalue, extrace = sys.exc_info()
            traceback.print_exception(extype, exvalue, extrace)

        return complexity
