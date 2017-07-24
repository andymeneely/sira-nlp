"""
@AUTHOR: meyersbs
"""

import traceback
import sys

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

import app.queryStrings as qs

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

    def handle(self, *args, **options):
        """

        """
        processes = options['processes']
        begin = dt.now()
        try:
            review_ids = {
                    2008: [], 2009: [], 2010: [], 2011: [], 2012: [], 2013: [],
                    2014: [], 2015: [], 2016: []
                }
            print("REVIEWS:")
            for i in review_ids.keys():
                review_ids[i] = list(qs.query_by_year(i, 'review', ids=True))
                print("\t{0}: {1}".format(str(i), str(len(review_ids[i]))))
                connections.close_all()


            comment_ids = {
                    2008: [], 2009: [], 2010: [], 2011: [], 2012: [], 2013: [],
                    2014: [], 2015: [], 2016: []
                }
            message_ids = {
                    2008: [], 2009: [], 2010: [], 2011: [], 2012: [], 2013: [],
                    2014: [], 2015: [], 2016: []
                }
            for year, ids in review_ids.items():
                comment_ids[year] = list(qs.query_by_year(year, 'comment', ids=True))
                connections.close_all()
                message_ids[year] = list(qs.query_by_year(year, 'message', ids=True))
                connections.close_all()

            print("COMMENTS:")
            for k, v in comment_ids.items():
                print("\t{0}: {1}".format(str(k), str(len(v))))

            print("MESSAGES:")
            for k, v in message_ids.items():
                print("\t{0}: {1}".format(str(k), str(len(v))))

            comment_sentences_ids = {
                    2008: [], 2009: [], 2010: [], 2011: [], 2012: [], 2013: [],
                    2014: [], 2015: [], 2016: []
                }
            message_sentences_ids = {
                    2008: [], 2009: [], 2010: [], 2011: [], 2012: [], 2013: [],
                    2014: [], 2015: [], 2016: []
                }

            print("COMMENT_SENTENCES:")
            for year, ids in comment_ids.items():
                comments = Comment.objects.filter(id__in=ids)
                connections.close_all()
                for c in comments:
                    comment_sentences_ids[year] += list(c.sentences.values_list('id'))
                print("\t{0}: {1}".format(str(year), str(len(comment_sentences_ids[year]))))
#            for year, ids in comment_ids.items():
#                comment_sentences_ids[year] = list(CommentSentences.objects.filter(comment_id__in=ids).values_list('sentence_id', flat=True))
#                connections.close_all()
#                print("\t{0}: {1}".format(str(year), str(len(comment_sentences_ids[year]))))

            print("MESSAGE_SENTENCES:")
            for year, ids in message_ids.items():
                messages = Message.objects.filter(id__in=ids)
                connections.close_all()
                for m in messages:
                    message_sentences_ids[year] += list(m.sentences.values_list('id'))
                print("\t{0}: {1}".format(str(year), str(len(message_sentences_ids[year]))))
#            for year, ids, in message_ids.items():
#                message_sentences_ids[year] = list(MessageSentences.objects.filter(message_id__in=ids).values_list('sentence_id', flat=True))
#                connections.close_all()
#                print("\t{0}: {1}".format(str(year), str(len(message_sentences_ids[year]))))

            sentences = list(qs.query_all('sentence', ids=False).values_list('id', 'text'))
            connections.close_all()

            orphans = {
                    2008: [], 2009: [], 2010: [], 2011: [], 2012: [], 2013: [],
                    2014: [], 2015: [], 2016: []
                }
            duplicates = {
                    2008: [], 2009: [], 2010: [], 2011: [], 2012: [], 2013: [],
                    2014: [], 2015: [], 2016: []
                }
            for sentence in sentences:
                for year in review_ids.keys():
                    print("YEAR: {0}".format(str(year)))
                    if sentence[0] not in comment_sentences_ids[year] and sentence[0] not in message_sentences_ids[year]:
                        orphans[year].append(sentence[0])
                    elif sentence[0] in comment_sentences_ids[year] and sentence[0] in message_sentences_ids[year]:
                        duplicates[year].append(sentence[0])

            print("================")
            print("ORPHANS:")
            for year, ids in orphans.items():
                print("\t{0}: {1}".format(str(year), str(len(ids))))

            print("DUPLICATES:")
            for year, ids in duplicates.items():
                print("\t{0}: {1}".format(str(year), str(len(ids))))

            connections.close_all()

        except KeyboardInterrupt:
            logger.warning('Attempting to abort...')
        finally:
            logger.info('Time: {:.2f} minutes.'
                .format(helpers.get_elapsed(begin, dt.now())))
