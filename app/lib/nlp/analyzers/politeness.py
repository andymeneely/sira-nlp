import sys
import traceback

from json import JSONDecodeError

import requests

from requests.exceptions import RequestException

from app.lib.nlp import analyzers

HEADERS = {'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'}
PARAMS = {'properties': "{'annotators': 'sentiment'}"}

DEFAULT_POLITENESS = {'polite': 0, 'impolite': 0}


class PolitenessAnalyzer(analyzers.Analyzer):
    def __init__(self, text, url='http://localhost:9000/'):
        super(PolitenessAnalyzer, self).__init__(text, parses, sents)
        self.url = url

    def analyze(self):
        politeness = DEFAULT_POLITENESS.copy()
        if self.text.strip() == '':
            return politeness

        try:
            response = requests.post(
                    self.url, params=PARAMS, headers=HEADERS,
                    data={'sentences': self.sents, 'parses': self.parses}.encode('UTF-8')
                )
            response.raise_for_status()
            for sentence in response.json()['sentences']:
                sentiment[CORENLP_MAP[sentence['sentimentValue']]] += 1
        except (JSONDecodeError, RequestException) as error:
            sys.stderr.write('Exception\n')
            sys.stderr.write('  Text: {}\n'.format(self.text[:50]))
            extype, exvalue, extrace = sys.exc_info()
            traceback.print_exception(extype, exvalue, extrace)
            return sentiment

        return sentiment
