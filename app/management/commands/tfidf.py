"""
@AUTHOR: meyersbs
"""

import csv
import glob
import operator
import os

from math import log10
from datetime import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from app.lib.files import *
from app.lib.helpers import *
from app.lib.logger import *
from app.lib.rietveld import *
from app.queryStrings import *


class Command(BaseCommand):
    """
    Sets up the command line arguments.
    """
    help = 'Calculate and display the tf-idf score for a single code review ' \
           ' or all code reviews created in a specified year.'

    def add_arguments(self, parser):
        """

        """
        parser.add_argument(
                '-id', type=int, default=None, help='Code review identifier '
                'of a code review to calculate tf-idf.'
            )
        parser.add_argument(
                '-year', type=int, default=None, help='tf-idf of all code '
                'reviews created in the specified year will be aggregated. '
                'Argument is ignored when id is specified.'
            )
        parser.add_argument(
                'term', type=str, default=None, help='The term to calculate '
                'tf-idf for.'
            )

    def handle(self, *args, **options):
        """

        """
        id = options.get('id', None)
        year = options.get('year', None)
        term = options.get('term', None)

        if term is None:
            raise CommandError('term must be specified')

        if id is None and year is None:
            raise CommandError('id or year must be provided')

        begin = dt.now()
        #files = Files(settings)
        reviews = {}
        try:
            if id is not None:
                tf = queryTermFrequency(term, id)
                df = queryDocumentFrequency(term)
                total = queryTotalDocuments()

                # +1 to pad result against df==0
                idf = log10(float(total)/float(df + 1))
                tf_idf = float(tf) * float(idf)

                info("TF-IDF for term \'%s\' in review %i is %3.3f." % \
                    (term,id,tf_idf))
            else:
                revIDs = queryReviewsByYear(year)
                df = queryDocumentFrequency(term, year)
                total = queryTotalDocuments(year)

                # +1 to pad result against df==0
                idf = log10(float(total)/float(df + 1))

                info('TF-IDF for reviews from %i:' % year)
                skipped = 0
                for r in revIDs:
                    tf = queryTermFrequency(term, r)
                    tf_idf = float(tf) * float(idf)

                    if tf_idf == 0:
                        skipped += 1
                    else:
                        info("TF-IDF for term \'%s\' in review %i is %3.3f." % \
                            (term,r,tf_idf))

                info("Skipped %i reviews where TF-IDF was 0" % skipped)
        except KeyboardInterrupt:
            warning('Attempting to abort.')
        finally:
            info('Time: {:.2f} mins'.format(get_elapsed(begin, dt.now())))
