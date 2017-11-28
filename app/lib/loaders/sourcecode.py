import multiprocessing
import re
import sys
import traceback

from django.db import Error, transaction

from app.lib import helpers, loaders
from app.lib.nlp import summarizer, sentenizer
from app.lib.utils import parallel
from app.models import *
from app.queryStrings import *

def _fix_join(text):
    text = re.sub(r' : ([\(\)])', r' :\1', text) # Smiley/Frowny Face
    text = re.sub(r' ([,.:;!?])', r'\1', text) # General Punctuation
    text = re.sub(r' \( \)', '', text) # Remove Function Calls
    text = re.sub(r'\( ', '(', text) # Clean Up Extra Spaces
    text = re.sub(r' \)', ')', text) # Clean Up Extra Spaces
#    text = re.sub(r" ('[a-zA-Z])", r"\1", text)

    return text

def _truncate(tokens):
    truncated_sent = list()
    last_is_code = False
    for (token, position, is_code) in tokens:
        if not is_code:
            truncated_sent.append(token)
            last_is_code = False
        else:
            if not last_is_code:
                truncated_sent.append("**CODE**")
                last_is_code = True
            else:
                pass

    return _fix_join(" ".join(truncated_sent)), truncated_sent

def _check_sent(tokens):
    no_code = list(filter(lambda a: a != "**CODE**", tokens))
    status = re.search(r'[a-zA-Z]', " ".join(no_code))
    return status

def aggregate(oqueue, cqueue, num_doers):
    count, done = 0, 0
    while True:
        item = cqueue.get()
        if item == parallel.DD:
            done += 1
            if done == num_doers:
                break
            continue  # pragma: no cover
        count += item
    oqueue.put(count)


def do(iqueue, cqueue):  # pragma: no cover
    while True:
        item = iqueue.get()
        if item == parallel.EOI:
            cqueue.put(parallel.DD)
            break

        (sent_id, tokens) = item

        count = 0
        with transaction.atomic():
            try:
                sorted_tokens = sorted(tokens, key=lambda x: x[1])
                truncated_sentence, truncated_tokens = _truncate(sorted_tokens)
                print(truncated_sentence)
                sent = Sentence.objects.get(id=sent_id)
                sent.clean_text = truncated_sentence
                #if _check_sent(truncated_tokens):
                #    sent.is_code = True
                    #print(True)
                #else:
                #    pass
                sent.save()
                count += 1
            except Error as err:  # pragma: no cover
                sys.stderr.write('Exception\n')
                sys.stderr.write('  Sentence  {}\n'.format(sent_id))
                extype, exvalue, extrace = sys.exc_info()
                traceback.print_exception(extype, exvalue, extrace)

        cqueue.put(count)


def stream(sentence_ids, settings, iqueue, num_doers):
    for sent_id in sentence_ids:
        tokens = Token.objects.filter(sentence_id=sent_id).values_list(
                     'token', 'position', 'is_code')

        iqueue.put((sent_id, list(tokens)))

    for i in range(num_doers):
        iqueue.put(parallel.EOI)


class SourceCodeSentenceLoader(loaders.Loader):
    def __init__(self, settings, num_processes, sentence_ids):
        super(SourceCodeSentenceLoader, self).__init__(settings, num_processes)
        self.sentence_ids = sentence_ids

    def load(self):
        iqueue = parallel.manager.Queue(self.settings.QUEUE_SIZE)

        process = self._start_streaming(iqueue)
        count = parallel.run(do, aggregate, iqueue, self.num_processes)
        process.join()

        return count

    def _start_streaming(self, iqueue):
        process = multiprocessing.Process(
                target=stream,
                args=(
                    self.sentence_ids, self.settings, iqueue, self.num_processes
                )
            )
        process.start()

        return process
