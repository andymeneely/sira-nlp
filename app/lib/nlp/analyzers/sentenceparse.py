import sys
import traceback

from json import decoder
from simplejson import scanner

import collections
import requests

from requests.exceptions import RequestException

from app.lib.nlp import analyzers

HEADERS = {'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'}
PARAMS = {'properties': "{'annotators': 'tokenize,ssplit,pos,parse,depparse'}"} #,depparse'}"}

DEFAULT_PARSE = {'deps': [], 'trees': []}

class SentenceParseAnalyzer(analyzers.Analyzer):
#    def __init__(self, text, url='http://overkill.main.edu.rit.edu:41194'):
    def __init__(self, text, url='http://localhost:41194/'):
#    def __init__(self, text, url='http://archeology.gccis.rit.edu:9000/'):
#    def __init__(self, text, url='http://magnycours-02.main.ad.rit.edu:41194/'):
        super(SentenceParseAnalyzer, self).__init__(text)
        self.url = url

    def analyze(self):
        parse = DEFAULT_PARSE.copy()
        if self.text.strip() == '':
            return parse

        try:
            response = requests.post(
                    self.url, params=PARAMS, headers=HEADERS,
                    data=self.text.encode('UTF-8')
                )
            response.raise_for_status()
            for sentence in response.json()['sentences']:
                parse['trees'] = sentence['parse']
                parse['deps'] = sentence['enhancedPlusPlusDependencies']
#            return parse
        except (decoder.JSONDecodeError, RequestException,
                scanner.JSONDecodeError) as error:  # pragma: no cover
            sys.stderr.write('Exception\n')
            sys.stderr.write('  Text: {}\n'.format(self.text[:50]))
            extype, exvalue, extrace = sys.exc_info()
            traceback.print_exception(extype, exvalue, extrace)
            parse = {'deps': 'X', 'trees': 'X'}

        return parse
