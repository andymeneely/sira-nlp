"""
@AUTHOR: meyersbs
"""

import csv
import gc
import random
import traceback

from datetime import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.db.models import Count, lookups, Lookup
from django.db.models.fields import Field

from app import COMPLEXITY_PATH
from app.lib import helpers, logger
from app.lib.nlp.BerkeleyParser import BerkeleyParser
from app.lib.nlp.complexity import *
from app.lib.nlp.sentenizer import NLTKSentenizer
from app.models import *
from app.queryStrings import *

from splat.complexity.idea_density import *

DECIMAL_PLACES = 100
PARSER = None

def run_all_analyses(message_ids, save=False):
    """ Collect all results into a dictionary. """

    results = run_syntactic_complexity(message_ids, save)

    return results

def run_syntactic_complexity_corenlp(parse_list):
    """
    This is a special function for putting the complexity results into the
    database. Use with caution!
    """

    new_list = []

    for treestring in parse_list:
        tree = re.sub(r'  ', ' ', treestring)
        tree = re.sub(r'\n', '', tree)
        tree = re.sub(r'ROOT', '', tree)
        new_list.append(tree)

    try:
        yngve = get_mean_yngve(new_list)
    except ZeroDivisionError:
        yngve = 'X'
    try:
        frazier = get_mean_frazier(new_list)
    except ZeroDivisionError:
        frazier = 'X'
    try:
        # calc_idea() returns the tuple, (mean, min, max) pdensity.
        pdensity = calc_idea(new_list)[0]
    except (ZeroDivisionError, IndexError):
        pdensity = 'X'

    return {'yngve': yngve, 'frazier': frazier, 'pdensity': pdensity}

def run_syntactic_complexity(message_ids, save=False, no_mID=False):
    global PARSER
    results = {}
    results_list = []
    for message in message_ids:
        text = ''
        if no_mID:
            text = message
            sents = NLTKSentenizer(text).execute()
            treestrings = BerkeleyParser(1).parse(sents)
        else:
            text = query_mID_text(message)
            sents = NLTKSentenizer(text).execute()
            treestrings = PARSER.parse(sents)
            print('Got treestrings!')
        try:
            yngve = get_mean_yngve(treestrings)
        except ZeroDivisionError:
            yngve = 0
        try:
            frazier = get_mean_frazier(treestrings)
        except ZeroDivisionError:
            frazier = 0
        try:
            # calc_idea() returns the tuple, (mean, min, max) pdensity.
            pdensity = calc_idea(treestrings)[0]
        except ZeroDivisionError:
            pdensity = 0

        results[message] = {'yngve': yngve, 'frazier': frazier,
                            'pdensity': pdensity}

        if no_mID:
            return results[message]

    if save:
        to_csv(results, 'yngve', 'frazier', 'pdensity')

    return results

def run_yngve_analysis(message_ids, save=False, parser=None):
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
            yngve = 0

        yngve_dict[message] = yngve

    print("Calc Yngve: " + str(helpers.get_elapsed(b, dt.now())))

    if save:
        to_csv(yngve_dict, 'yngve')

    return yngve_dict

def run_frazier_analysis(message_ids, save=False, parser=None):
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

def run_pdensity_analysis(message_ids, save=False, parser=None):
    logger.info('Running P-Density analysis for %i messages...'
                % len(message_ids))
    raise NotImplementedError('P-density has not been implemented yet.')

def run_cdensity_analysis(message_ids, save=False, parser=None):
    logger.info('Running C-Density analysis for %i messages...'
                % len(message_ids))
    raise NotImplementedError('C-density has not been implemented yet.')

def to_csv(results, key1, key2=None, key3=None):
    global DECIMAL_PLACES
#    logger.info('Saving %s and %s results to a CSV...' % (key1,key2))
    b = dt.now()
    m_ids = sorted(list(results.keys()))
    print("Sorting Results: " + str(helpers.get_elapsed(b, dt.now())))
    try:
        b = dt.now()
        with open(COMPLEXITY_PATH, 'a', newline='') as f:
            wr = csv.writer(f, delimiter=',', quotechar='/',
                            quoting=csv.QUOTE_MINIMAL)
            temp = ['message_id', key1]
            if key2 is not None:
                temp = temp + [key2]
            if key3 is not None:
                temp = temp + [key3]
            wr.writerow(temp)

            del temp

            c = 0
            rows = []
            for m in m_ids:
                temp = []
                if key3 is not None and key2 is not None:
                    temp = [m, round(results[m][key1], DECIMAL_PLACES),
                            round(results[m][key2], DECIMAL_PLACES),
                            round(results[m][key3], DECIMAL_PLACES)]
                elif key2 is not None:
                    temp = [m, round(results[m][key1], DECIMAL_PLACES),
                            round(results[m][key2], DECIMAL_PLACES)]
                else:
                    temp = [m, round(results[m], DECIMAL_PLACES)]

                rows.append(temp)
                del temp

                if len(rows) == 200:
                    wr.writerows(rows)
                    logger.warning('Collecting garbage...')
                    rows = []
                    gc.collect()
                c += 1

            wr.writerows(rows)
            logger.warning('Collecting garbage...')
            rows = []
            gc.collect()

        print("Writing to CSV: " + str(helpers.get_elapsed(b, dt.now())))
        return True
    except Exception as e:
        logger.error(e)
        traceback.print_exc()
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
                'syntactic', 'frazier'], help='Specify the type of complexity '
                'analysis to run. If unspecified, all available analyses will '
                'be executed.')
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
            pop_message_ids = [12831,12830,12829,12828,10936,10935,10934,10933,10136,10137,10135,9230,9231,9229,9857,9856,9855,8969,8970,8968,10257,10258,9253,9251,9252,9250,8935,10496,10423,10424,10425,10422,6703,6702,6701,6700,6698,6699,1674,1673,4549,4548,4597,4596,5746,5747,5745,1346,1302,1054,1053,1047,1048,2117,2116,1915,1914,70660,70662,70661,70659,70571,70570,70998,70999,71011,71004,71005,71006,71007,71008,71009,71002,70997,71010,71003,70830,70831,70829,69268,69267,69265,69264,69263,69262,69266,68961,68960,68461,68460,68458,68457,68454,68455,68456,68459,68453,65635,65636,65633,65634,67600,67484,64884,67674,67034,67033,67465,67464,63499,63498,64304,64303,62010,62008,62007,62009,58552,58551,61625,61624,60766,60765,29577,29576,3749422,3749421,3798769,3798771,3798766,751798,751801,751807,751805,751804,751803,751802,751800,751799,751797,751806,751796,744433,744430,744431,744432,744429,3891400,3891401,3891402,3891404,3891405,3891406,3891407,3891408,3891409,3891410,3891411,3891403,3900357,3900355,3900354,3900356,3900358,2408940,3912819,3912818,3912817,3912806,3912802,3912804,3912805,3912808,3912809,3912810,3912811,3912812,3912813,3912814,3912815,3912816,3912800,3912801,3912803,3912807,2523990,3944728,3944727,3944732,3944729,3944730,3944731,3944733,3944734,3944735,3944736,3945344,2818000,2818002,2818004,2818005,2818006,2818007,2818008,2818010,2818009,2818001,2818003,2817588,2817587,2817586,2817585,2809093,2809095]
            #pop_message_ids = query_mIDs(population)
            #print("Gathering IDs: " + str(helpers.get_elapsed(b, dt.now())))

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
                        'syntactic': run_syntactic_complexity}

            if analysis in ANALYSES.keys():
                # The number of threads for the Berkeley Parser is hardcoded
                # to 1 because setting to any of the other accepted values
                # (1-4) causes timeouts.
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
