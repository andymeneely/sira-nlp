import json
import random
import re
import sys
import subprocess
import traceback

from json import JSONDecodeError

from app.lib.nlp import analyzers

from app.lib.external.uncertainty.model import *

DEFAULT_UNCERTAINTY = {"sent": 'X', "words": []}

class UncertaintyAnalyzer(analyzers.Analyzer):
    def __init__(self, text):
        super(UncertaintyAnalyzer, self).__init__(text)

    def analyze(self):
        uncertainty = DEFAULT_UNCERTAINTY.copy()
        if self.text.strip() == '':
            return uncertainty

        # Dump the string to a file
        temp_file = str(random.randint(1,10000)) + ".temp"
        try:
            with open(temp_file, "w") as f:
                f.write(self.text)
            # Generate Uncertainty Features
            features(temp_file)
            # Get Uncertainty
            uncertainty["sent"] = classify('sent', temp_file + ".tsv", binary=False)[1][0]
            uncertainty["words"] = classify('cue', temp_file + ".tsv", binary=False)[1]
        except Exception as error: # pragma: no cover
            sys.stderr.write('Exception\n')
            sys.stderr.write('  Text: {}\n'.format(self.text[:50]))
            extype, exvalue, extrace = sys.exc_info()
            traceback.print_exception(extype, exvalue, extrace)
            uncertainty = {'ERROR': str(extype)}
        finally:
            if os.path.exists(temp_file + ".tsv"):
                os.remove(temp_file + ".tsv")
            if os.path.exists(temp_file):
                os.remove(temp_file)

        return uncertainty
