import re
import sys
import traceback
import unicodedata

from json import decoder, loads
from simplejson import scanner, encoder

import requests

from requests.exceptions import RequestException

from app.lib.helpers import JSON_NULL, to_json
from app.lib.nlp import analyzers

HEADERS = {'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'}
PARAMS = {
        'properties':
        "{'annotators': 'sentiment', 'ssplit.isOneSentence': 'true'}"
    }

DEFAULT_SENTIMENT = {'vpos': JSON_NULL, 'pos': JSON_NULL, 'neut': JSON_NULL,
                     'neg': JSON_NULL, 'vneg': JSON_NULL}
CORENLP_MAP = {'0': 'vneg', '1': 'neg', '2': 'neut', '3': 'pos', '4': 'vpos'}

session = requests.Session()


class SentimentCleanAnalyzer(analyzers.Analyzer):
#    def __init__(self, text, url='http://interlagos-02.main.ad.rit.edu:41194/'):
#    def __init__(self, text, url='http://localhost:41194/'):
#    def __init__(self, text, url='http://overkill.main.ad.rit.edu:41194/'):
    def __init__(self, text, url=None):
        super(SentimentCleanAnalyzer, self).__init__(text)
        #print(url)
        if url is None:
            self.url = 'http://localhost:41194/'
        else:
            self.url = url

    def analyze(self):
        sentiment = DEFAULT_SENTIMENT.copy()
        if self.text.strip() == '':
            return sentiment

        try:
            response = session.post(
                    self.url, params=PARAMS, headers=HEADERS,
                    data=self.text.encode('UTF-8')
                )
            response.raise_for_status()
            for sentence in to_json(response.text)['sentences']:
                key = CORENLP_MAP[sentence['sentimentValue']]
                if sentiment[key] == JSON_NULL:
                    sentiment[key] = 1
                else:
                    sentiment[key] += 1
        except (decoder.JSONDecodeError, RequestException,
                scanner.JSONDecodeError) as error:  # pragma: no cover
            sys.stderr.write('Exception\n')
            sys.stderr.write('  Text: {}\n'.format(self.text[:50]))
            extype, exvalue, extrace = sys.exc_info()
            traceback.print_exception(extype, exvalue, extrace)

        types = [str(type(v)) for v in sentiment.values()]
        if "<class 'int'>" in types:
            for k, v in sentiment.copy().items():
                if v == JSON_NULL:
                    sentiment[k] = 0
        return sentiment
