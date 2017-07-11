"""
@AUTHOR: nuthanmunaiah
@AUTHOR: meyersbs
"""

import csv
import json
import os
import random
import re
import time

from collections import OrderedDict

import requests

from app.lib import patch

# Match the line of header that marks the beginning of quoted text.
# E.g., On 2008/01/01 00:00:01, Raymond Reddington wrote:
RESPONSE_HEAD_RE = re.compile('^On .* wrote:$\n', flags=re.MULTILINE)
# Match lines of quoted text.
# E.g., > Happy New Year
QUOTED_TEXT_RE = re.compile('^>+ ?.*$', flags=re.MULTILINE)
# Match code review diff location along with a line of contextual content.
# E.g., http://codereview.chromium.org/15076/diff/1/6
#       File chrome/browser/net/dns_master.cc (right):
CODEREVIEW_URL_RE = re.compile(  # pragma: no cover
        '^https?:\/\/(codereview.chromium.org|chromiumcodereview.appspot.com)'
        '\/\d+\/diff\/.*\n.*\n', flags=re.MULTILINE
    )

# Subsequent new lines
NEWLINES_RE = re.compile('(^$\n)+', flags=re.MULTILINE)
# Match unicode NULL character sequence
NULL_RE = re.compile(r'(\\|\\\\)u0000')
# Match the bug ID(s) in the code review description
BUG_ID_RE = re.compile('BUG=(.*)')
# Bug identifiers can have one of the following patterns prefixed or suffixed
# to them. These patterns are replaced with '' when parsing identifiers.
# E.g., chromium:123,http://crbug.com/123,123.
# NOTE: DO NOT change the sequence.
BUG_ID_PATTERNS = [
    'http://crbug.com/',
    'https://code.google.com/p/chromium/issues/detail?id=',
    'chromium:',
    '.'
]
JSON_NULL = json.dumps(None)


def enumerate_iter(iterable, offset=0, step=1):
    index = offset
    for element in iterable:
        yield index, element
        index += step


def chunk(lst, size):
    """ Break the specified list up into smaller lists of the given size. """
    for index in range(0, len(lst), size):
        yield lst[index:index + size]


def clean(text):
    """ Return the specified text with certain metadata removed. """
    text = RESPONSE_HEAD_RE.sub('', text)
    text = QUOTED_TEXT_RE.sub('', text)
    text = CODEREVIEW_URL_RE.sub('', text)
    text = NEWLINES_RE.sub('\n', text)
    return text


RE_1 = re.compile('(^[^>]*$)', flags=re.MULTILINE)
RE_2 = re.compile('(\n.*)$', flags=re.MULTILINE)
#RE_2 = re.compile('(\n[^\n]*)$', flags=re.MULTILINE)
RE_3 = re.compile('(> ){2,}')


def get_quoted_text(text):
    #print("==== initial\n" + str(repr(text)))
    # STEP 1: Remove the initital RESPONSE_HEAD
    temp1 = RESPONSE_HEAD_RE.sub('', text)
    #print("==== temp1\n" + str(repr(temp1)))

    # STEP 2: Replace XML-like tags with nonstandard characters that are
    #   unlikely to appear in natural or programming language. Note that in
    #   r'⦋\1⦌', the brackets are not standard square brackets, but instead
    #   U+298B and U+298C, respectively.
    temp1 = re.sub(r'<([^>]*)>', r'⦋\1⦌', temp1)
    #print("==== temp1\n" + str(repr(temp1)))

    # STEP 3: Find the non-quoted text.
    temp2 = RE_1.findall(temp1)
    #print("==== temp2\n" + str(repr(temp2)))

    # STEP 4: Get the quoted text, including multi-level quotes.
    temp3 = temp1.replace("".join(temp2), '')
    #print("==== temp3\n" + str(repr(temp3)))

    # STEP 5: Remove empty strings from the quoted text.
    temp4 = filter(None, RE_2.split(temp3))
    #print("==== temp4\n" + str(temp4))

    # STEP 6: Remove all lines starting with 2 or more consecutive instances of
    #   the pattern '> '. In other words, remove the multi-level quotes,
    #   leaving a list of lines from the most recent (top-level) quote.
    temp5 = []
    for line in temp4:
        #print(repr(line))
        temp_results = RE_3.search(line)
        #print(temp_results)
        if temp_results is None:
            temp6 = re.sub(r'^> ', '', line, 1, flags=re.MULTILINE)
            #print("==== temp6\n" + str(repr(temp6)))
            temp5.append(temp6)
    #print("==== temp5\n" + str(repr(temp5)))

    # STEP 7: Convert the resultsof STEP 6 to a raw string.
    text = "".join(temp5)
    #print("==== text\n" + str(repr(text)))

    # STEP 8: Remove any remaining RESPONSE_HEAD and strip trailing newlines.
    text = RESPONSE_HEAD_RE.sub('', text).rstrip("\n")
    #print("==== text\n" + str(repr(text)))

    # STEP 9: Undo the substitution from STEP 2.
    text.replace('⦋', '<')
    text.replace('⦌', '>')
    #print("==== final\n" + str(repr(text)))

    return text


def get_elapsed(begin, end):
    """
    Return the number of minutes that passed between the specified beginning
    and end.
    """
    return (end - begin).total_seconds() / 60


def get_json(url, parameters):
    """ Return the json associated with the given URL. """
    (status, json) = (None, None)
    response = requests.get(url, parameters, allow_redirects=False)
    status = response.status_code
    if status == requests.codes.ok:  # pragma: no cover
        json = response.json()

    return (status, json)


def get_row(model, *args, **kwargs):
    """
    This is a wrapper for a database lookup. Returns None if the specified
    model does not exist. For example, if you run `Review.objects.get(id=1234)`
    and the review with that ID doesn't exist, an exception will be raised.
    Instead, you can call `get_row(Review, id=1234)` and avoid exception
    handling elsewhere in the code base.
    """
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None


def get_verbs(filepath):
    """
    Return the contents of verbs file pointed to by the filepath argument as a
    dictionary in which the key is the conjugate of a verb and the value is
    uninflected verb form of the conjugate verb.

    For example, {'scolded': 'scold', 'scolding': 'scold'}

    Adapted from code provided in NodeBox:
    https://www.nodebox.net/code/index.php/Linguistics#verb_conjugation
    """
    verbs = dict()
    with open(filepath) as file:
        reader = csv.reader(file)
        for row in reader:
            for verb in row[1:]:
                verbs[verb] = row[0]

    return verbs


def load_json(filepath, sanitize=True):
    """ Load the specified json file after sanitizing it. """
    with open(filepath, 'r') as file:
        if sanitize:
            contents = file.read()
            contents = NULL_RE.sub('', contents)
            return json.loads(contents)
        return json.load(file)


def parse_bugids(text):
    """
    Search for bug IDs within the specified text. Return a list of any results.
    """
    ids = list()
    for match in BUG_ID_RE.finditer(text):
        for id in match.group(1).strip().split(','):
            for pattern in BUG_ID_PATTERNS:
                id = id.replace(pattern, '')
            id = to_int(id)
            if id is not None:
                ids.append(id)
    return ids


def sleep(seconds):
    """ Just a timer. """
    time.sleep(random.random() * seconds)


def sort(dictionary, by='value', cast=None, desc=False):
    """ Sort the specified dictionary by the specified value. """
    retrn = None

    if by not in ['key', 'value']:
        raise ValueError('Argument "by" can be "key" or "value"')
    if cast not in [None, int, float]:
        raise ValueError('Argument "cast" can be None, int or float')
    by = 1 if by == 'value' else 0

    items = sorted(
            dictionary.items(),
            key=lambda item: cast(item[by]) if cast is not None else item[by],
            reverse=desc
        )

    retrn = OrderedDict()
    for (key, value) in items:
        retrn[key] = value

    return retrn


def to_int(text):
    """
    Convert text to integer if conversion is posssible else return None.
    """
    try:
        return int(text)
    except ValueError:
        return None


def to_list(queue):
    """ Convert the specified queue to a list and return it. """
    list_ = list()
    if not queue.empty():
        while not queue.empty():
            list_.append(queue.get())
    return list_


def to_querystring(dictionary):
    """ Convert the specified dictionary to a query string and return it. """
    components = ['{}={}'.format(k, v) for (k, v) in dictionary.items()]
    return '&'.join(components)


def truncate(string, length=50):
    """
    If the specified string is less than (or equal to) the specified number of
    characters, return it. Otherwise, truncate the string, append an elipses
    (...) and return that.
    """
    return string[:length] + '...' if len(string) > length else string


def _get_related_chunks(chunk_a, patch_b):
    for chunk in patch_b.get_chunks():
        if chunk.get_base_hunk() == chunk_a.get_base_hunk():
            return chunk
    return None


def line_changed(line_number, patch_a, patch_b):
    a = patch.Patch(patch_a)
    b = patch.Patch(patch_b)
    c = a.get_chunk_by_line(line_number)
    d = _get_related_chunks(c, b)

    if d is None:
        return False

    e = c.get_lines()[line_number]
    f = d.get_hunk()
    g = d.get_lines()[f[2]+(f[3]-f[1])]

    if e != g:
        return True
    else:
        return False
