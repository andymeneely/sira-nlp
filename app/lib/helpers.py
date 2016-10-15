import json
import random
import time
from operator import itemgetter

import requests


def chunk(lst, size):
    for index in range(0, len(lst), size):
        yield lst[index:index + size]


def truncate(string, length=50):
    return string[:length] + '...' if len(string) > length else string


def normalize(paths, using):
    for key in paths:
        paths[key] = paths[key].format(base=using)
    return paths


def to_list(queue):
    list_ = list()
    if not queue.empty():
        while not queue.empty():
            list_.append(queue.get())
    return list_


def to_querystring(dictionary):
    components = ['{}={}'.format(k, v) for (k, v) in dictionary.items()]
    return '&'.join(components)


def get_json(url, parameters):
    (status, json) = (None, None)
    response = requests.get(url, parameters, allow_redirects=False)
    status = response.status_code
    if status == requests.codes.ok:
        json = response.json()

    return (status, json)


def get_elapsed(begin, end):
    return (end - begin).total_seconds() / 60


def sleep(seconds):
    time.sleep(random.random() * seconds)


def sort(dictionary, by='value', desc=True):
    if by not in ['key', 'value']:
        raise ValueError('The argument by must either be key or value')
    by = 1 if by == 'value' else 2
    return sorted(dictionary.items(), key=itemgetter(by), reverse=desc)


def get_row(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None
