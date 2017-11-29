import multiprocessing
import re
import sys
import traceback

from django.db import Error, transaction

from app.lib import helpers, loaders
from app.lib.nlp import summarizer, sentenizer, tokenizer
from app.lib.utils import parallel
from app.models import *
from app.queryStrings import *

CAMELCASE_RE = re.compile('([A-Z][a-z0-9]+){2,}')
CODECHARS_RE = re.compile('[<>\{\}\[\]\\~`_\=\+\^]')

def _fix_join(text):
    text = re.sub(r' : ([\(\)])', r' :\1', text) # Smiley/Frowny Face
    text = re.sub(r' ([,.:;!?])', r'\1', text) # General Punctuation
    text = re.sub(r' \( \)', '', text) # Remove Function Calls
    text = re.sub(r'\( ', '(', text) # Clean Up Extra Spaces
    text = re.sub(r' \)', ')', text) # Clean Up Extra Spaces

    return text

def _clean_tokens(tokens):
    clean_tokens = list()
    found_code = False
    for token in tokens:
        if (CODECHARS_RE.search(tok.token) is not None or
            CAMELCASE_RE.search(tok.token) is not None):
            clean_tokens.append('xxCODExx')
            found_code = True
        else:
            clean_tokens.append(token)

    return clean_tokens, found_code

def _truncate(tokens):
    truncated_sent = list()
    last_is_code = False
    for (token, position, is_code) in tokens:
        if not is_code:
            truncated_sent.append(token)
            last_is_code = False
        else:
            if not last_is_code:
                truncated_sent.append("xxCODExx")
                last_is_code = True
            else:
                pass

    return _fix_join(" ".join(truncated_sent)), truncated_sent

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

        (sent_id) = item

        count = 0
        with transaction.atomic():
            try:
                sent = Sentence.objects.get(id=sent_id)
                tokens = tokenizer.NLTKTokenizer(sent.text).execute()
                clean_tokens, found_code = _clean_tokens(tokens)
                if found_code:
                    truncated_sentence, truncated_tokens = _truncate(clean_tokens)
                    print(truncated_sentence)
                    sent.clean_text = truncated_sentence
                    sent.save()
                    count += 1
                else:
                    pass
            except Error as err:  # pragma: no cover
                sys.stderr.write('Exception\n')
                sys.stderr.write('  Sentence  {}\n'.format(sent_id))
                extype, exvalue, extrace = sys.exc_info()
                traceback.print_exception(extype, exvalue, extrace)

        cqueue.put(count)


def stream(sentence_ids, settings, iqueue, num_doers):
    for sent_id in sentence_ids:
        iqueue.put((sent_id))

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
