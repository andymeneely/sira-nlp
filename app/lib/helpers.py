import json
import random
import re
import time

from operator import itemgetter

import requests

# Match the line of header that marks the beginning of quoted text.
# E.g., On 2008/01/01 00:00:01, Raymond Reddington wrote:
RESPONSE_HEAD_RE = re.compile('^On .* wrote:$\n', flags=re.MULTILINE)
# Match lines of quoted text.
# E.g., > Happy New Year
QUOTED_TEXT_RE = re.compile('^>+ ?.*$', flags=re.MULTILINE)
# Match code review diff location along with a line of contextual content.
# E.g., http://codereview.chromium.org/15076/diff/1/6
#       File chrome/browser/net/dns_master.cc (right):
CODEREVIEW_URL_RE = re.compile(
        '^https?:\/\/(codereview.chromium.org|chromiumcodereview.appspot.com)'
        '\/\d+\/diff\/.*\n.*\n', flags=re.MULTILINE
    )
# Subsequent new lines
NEWLINES_RE = re.compile('(^$\n)+', flags=re.MULTILINE)
# Match unicode NULL character sequence
NULL_RE = re.compile(r'(\\|\\\\)u0000')


def chunk(lst, size):
    for index in range(0, len(lst), size):
        yield lst[index:index + size]


def clean(text):
    text = RESPONSE_HEAD_RE.sub('', text)
    text = QUOTED_TEXT_RE.sub('', text)
    text = CODEREVIEW_URL_RE.sub('', text)
    text = NEWLINES_RE.sub('\n', text)
    return text


def get_elapsed(begin, end):
    return (end - begin).total_seconds() / 60


def get_json(url, parameters):
    (status, json) = (None, None)
    response = requests.get(url, parameters, allow_redirects=False)
    status = response.status_code
    if status == requests.codes.ok:
        json = response.json()

    return (status, json)


def get_row(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None


def load_json(filepath, sanitize=True):
    with open(filepath, 'r') as file:
        contents = file.read()
        contents = NULL_RE.sub('', contents)
        return json.loads(contents)


def normalize(paths, using):
    for key in paths:
        paths[key] = paths[key].format(base=using)
    return paths


def sleep(seconds):
    time.sleep(random.random() * seconds)


def sort(dictionary, by='value', desc=True):
    if by not in ['key', 'value']:
        raise ValueError('The argument by must either be key or value')
    by = 1 if by == 'value' else 0
    return sorted(dictionary.items(), key=itemgetter(by), reverse=desc)


def to_list(queue):
    list_ = list()
    if not queue.empty():
        while not queue.empty():
            list_.append(queue.get())
    return list_


def to_querystring(dictionary):
    components = ['{}={}'.format(k, v) for (k, v) in dictionary.items()]
    return '&'.join(components)


def truncate(string, length=50):
    return string[:length] + '...' if len(string) > length else string
