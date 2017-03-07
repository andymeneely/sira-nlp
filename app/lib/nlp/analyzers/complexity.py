import sys
import traceback

from json import JSONDecodeError as JSONDE
from json.decoder import JSONDecodeError as DJSONDE

import requests

from requests.exceptions import RequestException

from app.lib.nlp import analyzers
from app.management.commands import complexity as comp

HEADERS = {'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'}
PARAMS = {'properties': "{'annotators': 'tokenize,ssplit,pos,parse'}"}

DEFAULT_COMPLEXITY = {'yngve': 0, 'frazier': 0,
                      'pdensity': 0, 'pdensity-min': 0, 'pdensity-max': 0,
                      'cdensity': 0, 'cdensity-min': 0, 'cdensity-max': 0}
FAILED_COMPLEXITY = {'yngve': 'JSONDecodeError', 'frazier': 'JSONDecodeError',
                     'pdensity': 'JSONDecodeError', 'pdensity-min': 'JSONDecodeError',
                     'pdensity-max': 'JSONDecodeError', 'cdensity': 'JSONDecodeError',
                     'cdensity-min': 'JSONDecodeError', 'cdensity-max': 'JSONDecodeError'}
DEFAULT_PARSE = []


class ComplexityAnalyzer(analyzers.Analyzer):
#    def __init__(self, text, url='http://interlagos-02.main.ad.rit.edu:9000'):
    def __init__(self, text, url='http://localhost:9000/'):
        super(ComplexityAnalyzer, self).__init__(text)
        self.url = url

    def analyze(self):
        complexity = DEFAULT_COMPLEXITY.copy()
        parse = DEFAULT_PARSE.copy()
        if self.text.strip() == '':
            return complexity, parse

        try:
            response = requests.post(
                    self.url, params=PARAMS, headers=HEADERS,
                    data=self.text.encode('UTF-8')
                )
            response.raise_for_status()
            parse_list = []
            try:
                for sentence in response.json()['sentences']:
                    parse_list.append(sentence['parse'].replace('\n', ''))

                complexity, parse = comp.run_syntactic_complexity_corenlp(parse_list)
            except (JSONDE, DJSONDE):
                complexity = FAILED_COMPLEXITY.copy()
                parse = 'JSONDecodeError'

        except Exception as error:
            sys.stderr.write('Exception\n')
            sys.stderr.write('  Text: {}\n'.format(self.text[:50]))
            extype, exvalue, extrace = sys.exc_info()
            traceback.print_exception(extype, exvalue, extrace)
        finally:
            return complexity, parse

        return complexity, parse
