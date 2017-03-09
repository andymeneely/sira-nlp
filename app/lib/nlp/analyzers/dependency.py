import sys
import traceback

from json import JSONDecodeError

import collections
import requests

from requests.exceptions import RequestException

from app.lib.nlp import analyzers

HEADERS = {'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'}
#PARAMS = {'properties': "{'annotators': 'tokenize,ssplit,pos,depparse', 'depparse.extradependencies': 'MAXIMAL', 'parse.originalDependencies': true, 'parse.model': 'edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz'}"}
PARAMS = {'properties': "{'annotators': 'tokenize,ssplit,pos,parse,depparse'}"}

DEFAULT_DEPENDENCY = {'deps': [], 'parse': []}

class DependencyAnalyzer(analyzers.Analyzer):
    def __init__(self, text, url='http://localhost:9000/'):
        super(DependencyAnalyzer, self).__init__(text)
        self.url = url

    def analyze(self):
        dependency = DEFAULT_DEPENDENCY.copy()
        if self.text.strip() == '':
            return dependency

        try:
            response = requests.post(
                    self.url, params=PARAMS, headers=HEADERS,
                    data=self.text.encode('UTF-8')
                )
            response.raise_for_status()
            for sentence in response.json()['sentences']:
#                print(sentence['parse'])
                dependency['parse'].append(sentence['parse'])
                for dep in sentence['enhancedPlusPlusDependencies']:
                    dependency['deps'].append(dep)
#                for parse in sentence['parse']:
#                    dependency['parse'].append(parse)
        except (JSONDecodeError, RequestException) as error:
            sys.stderr.write('Exception\n')
            sys.stderr.write('  Text: {}\n'.format(self.text[:50]))
            extype, exvalue, extrace = sys.exc_info()
            traceback.print_exception(extype, exvalue, extrace)
            return {'deps': 'X', 'parse': 'X'}

        return dependency
