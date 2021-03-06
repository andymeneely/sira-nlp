import sys
import traceback

from json import decoder
from simplejson import scanner

import collections
import requests

from requests.exceptions import RequestException

from app.lib.helpers import JSON_NULL, to_json
from app.lib.nlp import analyzers

HEADERS = {'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'}
PARAMS = {'properties': "{'annotators': 'tokenize,ssplit,pos,parse,depparse', 'ssplit.isOneSentence': 'true'}"} #,depparse'}"}

DEFAULT_PARSE = {'deps': [], 'trees': []}

class SentenceParseAnalyzer(analyzers.Analyzer):
#    def __init__(self, text, url='http://overkill.main.edu.rit.edu:41194'):
#    def __init__(self, text, url='http://localhost:41194/'):
#    def __init__(self, text, url='http://archeology.gccis.rit.edu:9000/'):
    def __init__(self, text, url=None): # pragma: no cover
        super(SentenceParseAnalyzer, self).__init__(text)
        #print(url)
        if url is None:
            self.url = 'http://localhost:41194/'
        else:
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
            for sentence in to_json(response.text)['sentences']:
                parse['trees'] = sentence['parse']
                parse['deps'] = sentence['enhancedPlusPlusDependencies']
#            return parse
        except (decoder.JSONDecodeError, RequestException,
                scanner.JSONDecodeError) as error:  # pragma: no cover
            sys.stderr.write('Exception\n')
            sys.stderr.write('  Text: {}\n'.format(self.text[:50]))
            extype, exvalue, extrace = sys.exc_info()
            traceback.print_exception(extype, exvalue, extrace)

        return parse
