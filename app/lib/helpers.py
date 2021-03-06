"""
@AUTHOR: nuthanmunaiah
@AUTHOR: meyersbs
"""

import codecs
import csv
import json
import os
import random
import re
import time
import unicodedata

from collections import OrderedDict
from splat.complexity import levenshtein_distance
from splat.corpora import *
from splat.Util import count_pronouns

import difflib
import pandas
import requests

import app.queryStrings as qs

from app.lib import patch, logger

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
NULL_RE = re.compile(r'\\+u0000')
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

# The two regular expressions that follow match components of the header text
# that is automatically inserted when a developer responds to a comment on
# Rietveld.
# E.g. On 2008/01/01 at 00:00:01, Raymond Reddington wrote:

# Match the date and time in header that is inserted to comment responses
# E.g. 2008/01/01 at 00:00:01
DATE_TIME_RE = re.compile(
        '(?P<date>\d{4}/\d{2}/\d{2})(?:\s|\sat\s)(?P<time>\d{2}:\d{2}:\d{2})'
    )
# Match the name of the author in header that is inserted to comment response
# E.g. Raymond Reddington
AUTHOR_RE = re.compile(', (.*) wrote:')


TOKENS = qs.query_all('token', ids=False)
PRONOUNS_1 = ['I', 'ME', 'MYSELF', 'MY', 'MINE', 'WE', 'US', 'OURSELVES', 'OUR',
              'OURS']
PRONOUNS_2 = ['YOU', 'YOURSELF', 'YOUR', 'YOURS', 'YOURSELVES']
PRONOUNS_3 = ['SHE', 'ITSELF', 'HER', 'HE', 'ITS', 'HIM', 'IT', 'HIMSELF',
              'HERSELF', 'HERS', 'HIS', 'THEY', 'THEM', 'THEMSELVES', 'THEIR',
              'THEIRS']

def get_syllable_count(tokens):
    total = 0
    pron = []
    for token in tokens:
        word = token.strip("\n")
        try:
            pron = CMUDICT[word.lower()]
        except KeyError:
            if re.search(r'[aeiouy]', word.lower()) is not None:
                closest_matches = difflib.get_close_matches(word.lower(), CMUDICT.keys(), 5)
                levs = {}
                for match in closest_matches:
                    l = levenshtein_distance(match, word.lower())
                    if l not in levs.keys(): levs[l] = []
                    levs[l].append(match)
                try:
                    min_lev = min(levs.keys())
                    closest = levs[min_lev][0]
                    pron = CMUDICT[closest]
                except:
                    pron = CMUDICT['to']
            else:
                pron = CMUDICT['to']

        temp_count = max([len(list(y for y in x if y[-1].isdigit())) for x in pron])

        if len(re.findall(r'[aeiouy]', word.lower())) == 1 and len(pron) > 1: total += 1
        else: total += temp_count

    return total

def get_type_token_ratio(tokens):
    toks = [ t[0] for t in tokens ]
    return len(list(set(toks))) / len(toks)

def get_pronoun_density(tokens):
    prn_1, prn_2, prn_3, prn_total = 0, 0, 0, 0
    for tok in tokens:
        if tok[1] in ["PRP", "PRP$", "WP", "WP$"]:
            prn_1 += 1 if tok[0].upper() in PRONOUNS_1 else 0
            prn_2 += 1 if tok[0].upper() in PRONOUNS_2 else 0
            prn_3 += 1 if tok[0].upper() in PRONOUNS_3 else 0

    prn_total = prn_1 + prn_2 + prn_3
    pronoun_density = {'1ST': prn_1/len(tokens), '2ND': prn_2/len(tokens),
                       '3RD': prn_3/len(tokens), 'TOT': prn_total/len(tokens)}
    return pronoun_density


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


def get_parent(raw, comments):
    """Return parent of a comment.

    Parameters
    ----------
    raw: str
        The raw text of the comment message for which the parent is to be
        identified.
    comments: list
        A list of instances of app.models.Comment representing the comments
        that have already been processed. The list is used to look for the
        parent of the comment represented by the raw text argument.

    Returns
    -------
    comment: object
        An instance of app.models.Comment that represents the parent of the
        comment specified using |raw|. None is returned if no parent was found.
    """
    match = RESPONSE_HEAD_RE.match(raw)
    if match is not None:
        # Extract date and time and author from comment reponse header
        header = match.group(0)

        match = DATE_TIME_RE.search(header)
        if match is None:
            logger.error('NONE: ' + raw)
            return None
        components = match.groupdict()
        timestamp = '{date} {time}'.format(
                date=components['date'].replace('/', '-'),
                time=components['time']
            )

        match = AUTHOR_RE.search(header)
        author = match.group(1)

        parents = list()
        for comment in comments:
            # Compare timestamps without milliseconds
            ind = len(comment.posted)
            if '.' in comment.posted:
                ind = comment.posted.index('.')
            if comment.posted[:ind] == timestamp:
                parents.append(comment)

        if len(parents) == 1:
            # Only one parent found by timestamp matching. Return it.
            return parents[0]
        else:
            # Multiple parents found by timestamp matching. Use full text.
            for comment in comments:
                text = '> {}'.format(comment.text.replace(r'\n', r'\n> '))
                if text in raw:
                    return comment
    return None if len(comments) == 0 else comments[-1]


def get_elapsed(begin, end):
    """
    Return the number of minutes that passed between the specified beginning
    and end.
    """
    return (end - begin).total_seconds() / 60


def get_file_experience(comment, reviews, comments):
    """Return review experience of author of comment at the file level.

    Parameters
    ----------
    comment: object
        An instance of app.models.Comment that contains the email address of
        the developer and the timestamp at which the comment was posted. The
        review experience metrics collected will include all reviews before the
        timestamp.
    reviews: object
        An instance of pandas.DataFrame that contains all reviews that were
        created before the comment being processed.
    comments:
        An instance of pandas.DataFrame that contains all comments that were
        posted before the comment being processed.

    Returns
    -------
    experience: dict
        A dictionary with two keys---uniform and proportional---with values
        being the review experience of a developer at the time the comment was
        posted. The review experience associated with the two keys (i.e.
        uniform and proportional) represent two variants of the review
        experience metrics that differ in the way contribution in a code review
        is quantified. In case of the uniform variant, all reviewers
        participating in a review are assumed to have contributed uniformly. In
        case of the proportional variant, the review contribution is
        proportional to the number of comments posted by a reviewer.
    """
    experience = None

    # Filters
    filter = reviews.reviewed_files.apply(lambda f: comment.file_path in f)
    reviews = reviews[filter]
    num_reviews, _ = reviews.shape
    reviews = reviews[reviews.reviewers.apply(lambda r: comment.author in r)]
    comments = comments[comments.review_id.isin(reviews.id)]
    comments = comments[comments.file_path == comment.file_path]

    if num_reviews > 0:
        experience = dict()
        (uniform, proportional) = _get_contribution(comment, reviews, comments)
        experience['uniform'] = uniform / num_reviews
        experience['proportional'] = proportional / num_reviews
    return experience


def get_json(url, parameters):
    """ Return the json associated with the given URL. """
    (status, json) = (None, None)
    response = requests.get(url, parameters, allow_redirects=False)
    status = response.status_code
    if status == requests.codes.ok:  # pragma: no cover
        json = response.json()

    return (status, json)


def get_module_experience(comment, reviews, comments):
    """Return review experience of author of comment at the module level.

    Parameters
    ----------
    comment: object
        An instance of app.models.Comment that contains the email address of
        the developer and the timestamp at which the comment was posted. The
        review experience metrics collected will include all reviews before the
        timestamp.
    reviews: object
        An instance of pandas.DataFrame that contains all reviews that were
        created before the comment being processed.
    comments:
        An instance of pandas.DataFrame that contains all comments that were
        posted before the comment being processed.

    Returns
    -------
    experience: dict
        A dictionary with two keys---uniform and proportional---with values
        being the review experience of a developer at the time the comment was
        posted. The review experience associated with the two keys (i.e.
        uniform and proportional) represent two variants of the review
        experience metrics that differ in the way contribution in a code review
        is quantified. In case of the uniform variant, all reviewers
        participating in a review are assumed to have contributed uniformly. In
        case of the proportional variant, the review contribution is
        proportional to the number of comments posted by a reviewer.
    """
    experience = None

    # Filters
    filter = reviews.reviewed_modules.apply(lambda m: comment.module_path in m)
    reviews = reviews[filter]
    num_reviews, _ = reviews.shape
    reviews = reviews[reviews.reviewers.apply(lambda r: comment.author in r)]
    comments = comments[comments.review_id.isin(reviews.id)]
    comments = comments[comments.module_path == comment.module_path]

    if num_reviews > 0:
        experience = dict()
        (uniform, proportional) = _get_contribution(comment, reviews, comments)
        experience['uniform'] = uniform / num_reviews
        experience['proportional'] = proportional / num_reviews
    return experience


def get_module_path(filepath):
    """Return module path deduced from a filepath"""
    return os.path.dirname(filepath)


def get_project_experience(comment, reviews, comments):
    """Return review experience of author of comment at the project level.

    Parameters
    ----------
    comment: object
        An instance of app.models.Comment that contains the email address of
        the developer and the timestamp at which the comment was posted. The
        review experience metrics collected will include all reviews before the
        timestamp.
    reviews: object
        An instance of pandas.DataFrame that contains all reviews that were
        created before the comment being processed.
    comments:
        An instance of pandas.DataFrame that contains all comments that were
        posted before the comment being processed.

    Returns
    -------
    experience: dict
        A dictionary with two keys---uniform and proportional---with values
        being the review experience of a developer at the time the comment was
        posted. The review experience associated with the two keys (i.e.
        uniform and proportional) represent two variants of the review
        experience metrics that differ in the way contribution in a code review
        is quantified. In case of the uniform variant, all reviewers
        participating in a review are assumed to have contributed uniformly. In
        case of the proportional variant, the review contribution is
        proportional to the number of comments posted by a reviewer.
    """
    experience = None

    # Filters
    num_reviews, _ = reviews.shape
    reviews = reviews[reviews.reviewers.apply(lambda r: comment.author in r)]
    comments = comments[comments.review_id.isin(reviews.id)]

    if num_reviews > 0:
        experience = dict()
        (uniform, proportional) = _get_contribution(comment, reviews, comments)
        experience['uniform'] = uniform / num_reviews
        experience['proportional'] = proportional / num_reviews
    return experience


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


def to_json(response):
    r = ''.join(
            char for char in response if unicodedata.category(char)[0] != "C"
        )
    return json.loads(r)

# Private Functions


def _get_contribution(comment, reviews, comments):
    # Variant: Uniform
    contribution = 1 / reviews.num_reviewers
    uniform = contribution.sum()

    # Variant: Proportional
    num_comments = pandas \
        .DataFrame({'count': comments.groupby('review_id').size()}) \
        .reset_index()
    comments = comments[comments.author == comment.author]
    num_authorcomments = pandas \
        .DataFrame({'count': comments.groupby('review_id').size()}) \
        .reset_index()

    merged = pandas.merge(
            num_authorcomments, num_comments, on='review_id',
            suffixes=('_ac', '_c')
        )
    contribution = merged.count_ac / merged.count_c
    proportional = contribution.sum()

    return (uniform, proportional)
