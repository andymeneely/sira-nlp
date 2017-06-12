import sys
import traceback

from json import decoder
from simplejson import scanner

import requests

from requests.exceptions import RequestException

from app.lib.nlp import analyzers

HEADERS = {'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'}
PARAMS = {'properties': "{'annotators': 'sentiment'}"}

DEFAULT_SENTIMENT = {'vpos': 0, 'pos': 0, 'neut': 0, 'neg': 0, 'vneg': 0}
CORENLP_MAP = {'0': 'vneg', '1': 'neg', '2': 'neut', '3': 'pos', '4': 'vpos'}

session = requests.Session()


class SentimentAnalyzer(analyzers.Analyzer):
#    def __init__(self, text, url='http://interlagos-02.main.ad.rit.edu:41194/'):
    def __init__(self, text, url='http://localhost:41194/'):
#    def __init__(self, text, url='http://overkill.main.ad.rit.edu:41194/'):
#    def __init__(self, text, url='http://archeology.gccis.rit.edu:9000/'):
        super(SentimentAnalyzer, self).__init__(text)
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
            for sentence in response.json()['sentences']:
                sentiment[CORENLP_MAP[sentence['sentimentValue']]] += 1
        except (decoder.JSONDecodeError, RequestException,
                scanner.JSONDecodeError) as error:  # pragma: no cove
            sys.stderr.write('Exception\n')
            sys.stderr.write('  Text: {}\n'.format(self.text[:50]))
            extype, exvalue, extrace = sys.exc_info()
            traceback.print_exception(extype, exvalue, extrace)
            return sentiment

        return sentiment
