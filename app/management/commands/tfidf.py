"""
@AUTHOR: meyersbs
"""

import csv
import math
import traceback

from datetime import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connections

from app import TFIDF_TOKENS_PATH, TFIDF_LEMMAS_PATH
from app.lib import helpers
from app.lib.logger import *
from app.lib.nlp import tfidf, tokenremover
from app.models import *
from app.queryStrings import *


def get_types(tfidfs, max_length, top):
    """
    Return unique types (tokens/lemmas) composed from multiple documents.

    Parameters
    ----------
    tfidfs: dict
        A dictionary with review identifier as key and the correponding value
        is either {'token': tfidf} or {'lemma': tfidf} of all token or lemma in
        the code review.
    max_length: int
        The maximum length of the types that must be included.
    top: int
        Number of types to select from each code review. The assumption is that
        the {'token': tfidf} or {'lemma': tfidf} dictionaries corresponding to
        each review identifier is order by tfidf. The assumption is enforced by
        app.lib.nlp.tfidf.

    Returns
    -------
    types: list
        A list of unique types identified from all reviews.
    """
    types = set()
    for tfidf in tfidfs.values():
        types |= set(
                tokenremover.TokenRemover(
                    tfidf.keys(), configuration={'WL': {'length': max_length}}
                ).execute()[:top]
            )
    return types


def write_csvs(tf_idfs, filepath, chunksize, types):
    """ Writer TF-IDF dictionary to one or more CSV files. """
    info('  Saving TF-IDF to a CSV file(s)')
    chunks = helpers.chunk(list(types), size=chunksize)
    for (index, chunk) in enumerate(chunks):
        _write_chunk(filepath.format(index), tf_idfs, set(chunk))


def _write_chunk(filepath, tfidfs, types):
    debug('_write_chunk: {}'.format(filepath))
    types_list = list(types)
    indices = {type_: index for (index, type_) in enumerate(types_list)}
    rows = [['review_id'] + types_list]
    for (r, tfidf) in tfidfs.items():
        row = [''] * len(types)
        for token in (set(tfidf.keys()) & types):
            row[indices[token]] = '{:.6e}'.format(tfidf[token])
        rows.append([r] + row)
    _write_csv(filepath, rows)


def _write_csv(filepath, rows):
    debug('_write_csv: {} {}'.format(filepath, len(rows)))
    with open(filepath, 'w', newline='') as f:
        wr = csv.writer(f)
        wr.writerows(rows)
        info('  {:,} row(s) written to {}'.format(len(rows), filepath))


def get_idf_dict(df, pop_num_docs, use_tokens=False):
    """
    Calculate the IDF for every token in the population.

    NOTE: At first glance, this may seem like it creates a lot of overhead, but
    at the end of the day, it really doesn't.
    """
    idf = dict()
    text = 'token' if use_tokens else 'lemma'
    for item in df:
        (_term, _df) = (item[text], item['df'])
        idf[_term] = math.log(float(pop_num_docs / _df))
    return idf


def load_tfidf_dict(review_ids, idf_dict, num_procs=8, use_tokens=False):
    """
    Call the multiprocessed commands for computing TF-IDF, and return the
    resulting nested dictionary of the form:

    {review_id:{token:score,...},...}
    """
    info('  Calculating TF-IDF for {:,} reviews'.format(len(review_ids)))
    tf_idfs = tfidf.compute(review_ids, idf_dict, num_procs, not use_tokens)
    return tf_idfs


def get_random_sample(population, pop_review_ids, rand):
    sample_review_ids = []

    if population == 'all':
        sample_review_ids += query_rIDs_random(query_rIDs_neutral(), rand)
        sample_review_ids += query_rIDs_random(query_rIDs_fixed(), rand)
        sample_review_ids += query_rIDs_random(query_rIDs_missed(), rand)
    elif population == 'fm':
        sample_review_ids += query_rIDs_random(query_rIDs_fixed(), rand)
        sample_review_ids += query_rIDs_random(query_rIDs_missed(), rand)
    elif population == 'nf':
        sample_review_ids += query_rIDs_random(query_rIDs_neutral(), rand)
        sample_review_ids += query_rIDs_random(query_rIDs_fixed(), rand)
    elif population == 'nm':
        sample_review_ids += query_rIDs_random(query_rIDs_neutral(), rand)
        sample_review_ids += query_rIDs_random(query_rIDs_missed(), rand)
    else:
        sample_review_ids += query_rIDs_random(pop_review_ids, rand)

    return sample_review_ids


class Command(BaseCommand):
    """ Sets up the command line arguments. """

    help = 'Calculate and display the tf-idf score for a single code review ' \
           ' or all code reviews created in a specified year.'

    def add_arguments(self, parser):
        """
        """
        parser.add_argument(
                '--processes', dest='processes', type=int,
                default=settings.CPU_COUNT,
                help='Number of processes to spawn. Default is {}'.format(
                        settings.CPU_COUNT
                    )
            )
        parser.add_argument(
                '--use-tokens', default=False, action='store_true',
                help='When set, TF-IDF will be calculated on tokens instead'
                     ' of lemmas.'
            )
        parser.add_argument(
                '--population', type=str, default='all',
                choices=['all', 'fm', 'nf', 'nm'],
                help='If unspecified, TF-IDF will be calculated against the '
                     'entire corpus of reviews. Default is all.'
            )
        parser.add_argument(
                '--chunksize', dest='chunksize', type=int, default=5000,
                help='Number of rows in each CSV chunk. Default is 1000.'
            )
        parser.add_argument(
                '--maxlength', dest='maxlength', type=int, default=35,
                help='Maximum length of the token/lemma to include in the'
                     'analysis. Default is 35.'
            )
        parser.add_argument(
                '--top', type=int, default=100,
                help='If specified, TF-IDF will only be calculated for the '
                'most frequent number of tokens provided. The default is to '
                'calculate for all tokens. Default is 100.'
            )
        parser.add_argument(
                '--random', type=float, default=None,
                help='If specified, a random sampling of the given size will '
                'be printed to stdout or saved to disk. Default is 1000.'
            )

    def handle(self, *args, **options):
        # Grab the command line arguments.
        processes = options['processes']
        use_tokens = options['use_tokens']
        population = options['population']
        chunksize = options['chunksize']
        max_length = options['maxlength']
        top = options['top']
        random = options['random']

        begin = dt.now()
        try:
            info('tfidf Command')

            pop_review_ids = query_rIDs(population)
            pop_num_docs = len(pop_review_ids)
            info('  Population has {:,} reviews'.format(pop_num_docs))

            sample_review_ids = pop_review_ids
            if random is not None:
                sample_review_ids = get_random_sample(
                        population, pop_review_ids, random
                    )
            sample_num_docs = len(sample_review_ids)

            info('  Computing the denominator of IDF')
            df = query_DF(pop_review_ids, use_tokens)

            info('  Computing the IDF in TF-IDF')
            idf = get_idf_dict(df, pop_num_docs, use_tokens)

            connections.close_all()  # Hack
            tfidfs = load_tfidf_dict(
                    sample_review_ids, idf, processes, use_tokens
                )

            types = get_types(tfidfs, max_length, top)
            info('  {:,} types chosen'.format(len(types)))
            filepath = TFIDF_TOKENS_PATH if use_tokens else TFIDF_LEMMAS_PATH
            write_csvs(tfidfs, filepath, chunksize, types)

            assert len(tfidfs) == sample_num_docs
        except KeyboardInterrupt:
            warning('Attempting to abort.')
        finally:
            info('Time: {:.2f} mins'.format(
                    helpers.get_elapsed(begin, dt.now())
                ))
