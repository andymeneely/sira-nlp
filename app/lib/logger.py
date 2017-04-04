"""
@AUTHOR: nuthanmunaiah
"""

import os
import sys

from termcolor import cprint

LAST_LOG = ""

def debug(message):
    """ Prepend '\r[DBG]' to the given message and print to stderr in blue. """
    global LAST_LOG
    if 'DEBUG' in os.environ: # pragma: no cover
        LAST_LOG = message
        cprint('\r[DBG] {0}'.format(message), 'blue', file=sys.stderr)
    else:
        LAST_LOG = message

def info(message):
    """ Prepend '\r[INF]' to the given message and print to stdout in white. """
    global LAST_LOG
    LAST_LOG = message
    cprint('\r[INF] {0}'.format(message), 'white', file=sys.stdout)


def warning(message):
    """
    Prepend '\r[WRN] ' to the specified message, make it yellow, and print to
    stderr.
    """
    global LAST_LOG
    LAST_LOG = message
    cprint('\r[WRN] {0}'.format(message), 'yellow', file=sys.stderr)


def error(message):
    """
    Prepend '\r[ERR] ' to the specified message, make it red, and print to
    stderr.
    """
    global LAST_LOG
    LAST_LOG = message
    cprint('\r[ERR] {0}'.format(message), 'red', file=sys.stderr)

def get_last_log():
    global LAST_LOG
    return LAST_LOG
