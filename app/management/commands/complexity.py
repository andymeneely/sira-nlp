"""
@AUTHOR: meyersbs
"""

import csv
import gc
import random

from datetime import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.db.models import Count, lookups, Lookup
from django.db.models.fields import Field

from app import YNGVE_PATH, FRAZIER_PATH, PDENSITY_PATH, CDENSITY_PATH
from app.lib import helpers, logger
from app.lib.nlp.BerkeleyParser import BerkeleyParser
from app.lib.nlp.complexity import *
from app.lib.nlp.sentenizer import NLTKSentenizer
from app.models import *
from app.queryStrings import *

DECIMAL_PLACES = 100
PARSER = None

def run_all_analyses(message_ids, save=False):
    """ Collect all results into a dictionary. """
    results_dict = {'ygnve': run_yngve_analysis(message_ids,save),
                    'frazier': run_frazier_analysis(message_ids,save),
                    'pdensity': run_pdensity_analysis(message_ids,save),
                    'cdensity': run_cdensity_analysis(message_ids,save)}

    return results_dict

def run_yngve_analysis(message_ids, save=False):
    global PARSER
    b = dt.now()
    logger.info('Running Ygnve analysis for %i messages...'
                % len(message_ids))
    yngve_dict = {}
    for message in message_ids:
        text = query_mID_text(message)
        sents = NLTKSentenizer(text).execute()
        treestrings = PARSER.parse(sents)
        try:
            yngve = get_mean_yngve(treestrings)
        except ZeroDivisionError:
            yngve = 0.0

        yngve_dict[message] = yngve

    print("Calc Yngve: " + str(helpers.get_elapsed(b, dt.now())))

    if save:
        to_csv(yngve_dict, 'yngve')

    return yngve_dict

def run_frazier_analysis(message_ids, save=False):
    global PARSER
    b = dt.now()
    logger.info('Running Frazier analysis for %i messages...'
                % len(message_ids))
    frazier_dict = {}
    for message in message_ids:
        text = query_mID_text(message)
        sents = NLTKSentenizer(text).execute()
        treestrings = PARSER.parse(sents)
        try:
            frazier = get_mean_frazier(treestrings)
        except ZeroDivisionError:
            frazier = 0

        frazier_dict[message] = frazier

    print("Calc Frazier: " + str(helpers.get_elapsed(b, dt.now())))

    if save:
        to_csv(frazier_dict, 'frazier')

    return frazier_dict

def run_pdensity_analysis(message_ids, save=False):
    global PARSER
    logger.info('Running P-Density analysis for %i messages...'
                % len(message_ids))
    raise NotImplementedError('P-density has not been implemented yet.')

def run_cdensity_analysis(message_ids, save=False):
    global PARSER
    logger.info('Running C-Density analysis for %i messages...'
                % len(message_ids))
    raise NotImplementedError('C-density has not been implemented yet.')

def to_csv(results, column):
    global DECIMAL_PLACES
    logger.info('Saving %s to a CSV...' % (column))
    path = {'yngve': YNGVE_PATH, 'frazier': FRAZIER_PATH,
            'pdensity': PDENSITY_PATH, 'cdensity': CDENSITY_PATH}
    b = dt.now()
    m_ids = sorted(list(results.keys()))
    print("Sorting Results: " + str(helpers.get_elapsed(b, dt.now())))
    try:
        b = dt.now()
        with open(path[column], 'a', newline='') as f:
            wr = csv.writer(f, delimiter=',', quotechar='/',
                            quoting=csv.QUOTE_MINIMAL)
            wr.writerow(['message_id', column])

            c = 0
            rows = []
            for m in m_ids:
                rows.append([m, round(results[m], DECIMAL_PLACES)])

                if len(rows) == 200:
                    wr.writerows(rows)
                    logger.warning('Collecting garbage...')
                    rows = []
                    gc.collect()
                c += 1

        print("Writing to CSV: " + str(helpers.get_elapsed(b, dt.now())))
        return True
    except Exception as e:
        logger.error(e)
        return False

def get_random_sample(population, pop_message_ids, rand):
    sample_message_ids = []

    if population == 'all':
        b = dt.now()
        sample_message_ids += query_mIDs_random(query_mIDs_neutral(), rand)
        sample_message_ids += query_mIDs_random(query_mIDs_fixed(), rand)
        sample_message_ids += query_mIDs_random(query_mIDs_missed(), rand)
        print("Getting Samples: " + str(helpers.get_elapsed(b, dt.now())))
    elif population == 'fm':
        b = dt.now()
        sample_message_ids += query_mIDs_random(query_mIDs_fixed(), rand)
        sample_message_ids += query_mIDs_random(query_mIDs_missed(), rand)
        print("Getting Samples: " + str(helpers.get_elapsed(b, dt.now())))
    elif population == 'nf':
        b = dt.now()
        sample_message_ids += query_mIDs_random(query_mIDs_neutral(), rand)
        sample_message_ids += query_mIDs_random(query_mIDs_fixed(), rand)
        print("Getting Samples: " + str(helpers.get_elapsed(b, dt.now())))
    elif population == 'nm':
        b = dt.now()
        sample_message_ids += query_mIDs_random(query_mIDs_neutral(), rand)
        sample_message_ids += query_mIDs_random(query_mIDs_missed(), rand)
        print("Getting Samples: " + str(helpers.get_elapsed(b, dt.now())))
    else:
        b = dt.now()
        sample_message_ids += query_mIDs_random(pop_message_ids, rand)
        print("Getting Samples: " + str(helpers.get_elapsed(b, dt.now())))

    gc.collect()

    return sample_message_ids

#@Field.register_lookup
class AnyLookup(lookups.In):
    def get_rhs_op(self, connection, rhs):
        return '= ANY(ARRAY(%s))' % rhs

class Command(BaseCommand):
    """ Sets up the command line arguments. """

    help = 'Calculate and display the syntactic complexity scores for a ' \
           'messages within a group of code review.'

    def add_arguments(self, parser):
        """
        """
        parser.add_argument(
                'analysis', type=str, default='all', choices=['all', 'yngve',
                'frazier', 'p-density', 'c-density'], help='Specify the type '
                'of syntactic complexity analysis to run. If unspecified, all '
                'available analyses will be executed.')
        parser.add_argument(
                '--pop', type=str, default='all', choices=['all', 'fixed',
                'missed', 'neutral', 'fm', 'nf', 'nm'], help='If specified, '
                'only messages within the given population will be printed to '
                'stdout or saved to disk.')
        parser.add_argument(
                '--save', default=False, action='store_true',
                help='If included, save the syntactic complexity scores to a '
                'CSV file. Else, print the results to stdout.')
        parser.add_argument(
                '--round', type=int, default=100, help="If specified,  "
                "complexity scores will be rounded to the given number of "
                "decimal places. The default is 100 (don't round).")
        parser.add_argument(
                '--rand', type=int, default=-1, help='If specified, a random '
                'sampling of the given size will be printed to stdout or '
                'saved to disk.')

    def handle(self, *args, **options):
        global DECIMAL_PLACES, ANALYSES, PARSER
        # Grab the command line arguments.
        analysis = options.get('analysis', 'all')
        save = options.get('save', False)
        DECIMAL_PLACES = options.get('round', 100)
        population = options.get('pop', 'all')
        rand = options.get('rand', -1)

        # Start the timer.
        start = dt.now()
        try:
            logger.info('Gathering message IDs...')
            pop_message_ids = None
            b = dt.now()
            pop_message_ids = query_mIDs(population)
            print("Gathering IDs: " + str(helpers.get_elapsed(b, dt.now())))

            pop_num_docs = len(pop_message_ids)

            sample_message_ids = pop_message_ids
            if rand > 0:
                sample_message_ids = get_random_sample(population, pop_message_ids, rand)

            sample_num_docs = len(sample_message_ids)

            # This is a hack. It closes all connections before running
            # parallel computations.
            connections.close_all()

            results = None

            ANALYSES = {'all': run_all_analyses,
                        'yngve': run_yngve_analysis,
                        'frazier': run_frazier_analysis,
                        'p-density': run_pdensity_analysis,
                        'c-density': run_cdensity_analysis}

            if analysis in ANALYSES.keys():
                PARSER = BerkeleyParser(1)
                results = ANALYSES[analysis](sample_message_ids, save)

            if not save:
                print(results)

            PARSER.deactivate()
        except KeyboardInterrupt:
            logger.warning('Attempting to abort...')
        finally:
            logger.info('Time: {:.2f} minutes.'
                .format(helpers.get_elapsed(start, dt.now())))
