import json
import os
import random
import re
import sys
import subprocess
import traceback

from json import JSONDecodeError

from app.lib.nlp import analyzers

from app.lib.external.uncertainty.model import *

DEFAULT_UNCERTAINTY = ["X", []]

def _aggregate_sent_label(token_labels):
    labs = {"C": 0, "U": 0, "I": 0, "N": 0, "E": 0, "D": 0}
    for label in token_labels:
        labs[label] += 1

    if (labs["U"] != 0 or labs["E"] != 0 or labs["I"] != 0 or
        labs["D"] != 0 or labs["N"] != 0):

        labs.pop("C", None)
        max_val = max(labs.values())
        max_keys = []

        for k, v in labs.items():
            if v == max_val:
                max_keys.append(k)

        if len(max_keys) == 1:
            return max_keys[0]
        else:
            return "U"
    else:
        return "C"

def _purge(temp_files): # pragma: no cover
    for file in temp_files:
        if os.path.exists(file + ".tsv"):
            os.remove(file + ".tsv")
        if os.path.exists(file):
            os.remove(file)

class UncertaintyAnalyzer(analyzers.Analyzer):
    def __init__(self, tokens):
        super(UncertaintyAnalyzer, self).__init__("")
        self.tokens = tokens

    def analyze(self):
        uncertainty = DEFAULT_UNCERTAINTY.copy()
        if len(self.tokens) == 0:
            return uncertainty

        temp_files = []
        try:
            for tok in self.tokens:
                temp_file = str(random.randint(1,10000)) + ".temp"
                temp_files.append(temp_file)
                with open(temp_file, "w") as f:
                    f.write(tok.token)
                features(temp_file)
                uncertainty[1].append(classify('cue', temp_file + ".tsv", binary=False))

            uncertainty[0] = _aggregate_sent_label(uncertainty[1])
        except Exception as error: # pragma: no cover
            sys.stderr.write('Exception\n')
            sys.stderr.write('  Text: {}\n'.format(self.text[:50]))
            extype, exvalue, extrace = sys.exc_info()
            traceback.print_exception(extype, exvalue, extrace)
            uncertainty = [str(extype), []]
        finally:
            _purge(temp_files)

        return uncertainty
