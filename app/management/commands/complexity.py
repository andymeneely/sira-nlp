"""
@AUTHOR: meyersbs
"""

import traceback
import sys
import time
import timeout_decorator

from json import JSONDecodeError

from datetime import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.db.models import Count, lookups, Lookup
from django.db.models.fields import Field

from app.lib import helpers, logger, taggers
from app.lib.nlp.complexity import *
from app.models import *

from splat.complexity.idea_density import *
from splat.complexity import *

#@timeout_decorator.timeout(30)
def get_syntactic_complexity(treeparse, use_signals=False):
    """
    This is a special function for putting the complexity results into the
    database. Use with caution!
    """

#    treeparse = "(S " + treeparse + " )"
    treeparse = [treeparse]
    try:
        yngve = get_mean_yngve(treeparse)
    except ZeroDivisionError:
        yngve = 'ZeroDivisionError'
    except JSONDecodeError:
        yngve = 'JSONDecodeError'
#    print("YNGVE")
    try:
        frazier = get_mean_frazier(treeparse)
    except ZeroDivisionError:
        frazier = 'ZeroDivisionError'
    except JSONDecodeError:
        frazier = 'JSONDecodeError'
#    print("FRAZIER")
    try:
        # calc_idea() returns the tuple, (mean, min, max) pdensity.
        result = calc_idea(treeparse)
        pdensity = result[0]
    except TypeError:
        pdensity = 'InvalidTreeString'
    except Exception:
        extype, _, _ = sys.exc_info()
        pdensity = str(extype)
#    print("PDENSITY")
    try:
        # calc_content() returns the tuple, (mean, min, max) cdensity.
        result = calc_content_density(treeparse)
        cdensity = result[0]
    except TypeError:
        cdensity = 'InvalidPOSTag'
    except Exception:
        extype, _, _ = sys.exc_info()
        cdensity = str(extype)
#    print("CDENSITY")

    return {'yngve': yngve, 'frazier': frazier, 'pdensity': pdensity,
            'cdensity': cdensity}

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
                '--processes', dest='processes', type=int,
                default=settings.CPU_COUNT, help='Number of processes to spawn.'
                ' Default is {}'.format(settings.CPU_COUNT)
            )
        parser.add_argument(
                '--condition', type=str, default='all', dest='condition',
                choices=['all', 'empty', 'failed'], help="The sentences to "
                "repopulate parses for. Defualt is 'all'."
            )

    def handle(self, *args, **options):
        """

        """
        processes = options['processes']
        condition = options['condition']
        begin = dt.now()
        try:
            sents = []
            if condition == 'all':
                sents = Sentence.objects.exclude(text='').iterator()
            elif condition == 'empty':
                sents = Sentence.objects.filter(metrics__complexity={}).exclude(text='').iterator()
            elif condition == 'failed':
                sents = Sentence.objects.filter(metrics__complexity={}).exclude(text='').iterator()

            connections.close_all()
            tagger = taggers.ComplexityTagger(settings, processes, sents)
            tagger.tag()

        except KeyboardInterrupt:
            logger.warning('Attempting to abort...')
        finally:
            logger.info('Time: {:.2f} minutes.'
                .format(helpers.get_elapsed(begin, dt.now())))
