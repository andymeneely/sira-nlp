"""
@AUTHOR: nuthanmunaiah
"""

import os
import sys

from termcolor import cprint


def debug(message):
    """ Prepend '\r[DBG]' to the given message and print to stderr in blue. """
    if 'DEBUG' in os.environ:
        cprint('\r[DBG] {0}'.format(message), 'blue', file=sys.stderr)


def info(message):
    """ Prepend '\r[INF]' to the given message and print to stdout in white. """
    cprint('\r[INF] {0}'.format(message), 'white', file=sys.stdout)


def warning(message):
    """
    Prepend '\r[WRN] ' to the specified message, make it yellow, and print to
    stderr.
    """
    cprint('\r[WRN] {0}'.format(message), 'yellow', file=sys.stderr)


def error(message):
    """
    Prepend '\r[ERR] ' to the specified message, make it red, and print to
    stderr.
    """
    cprint('\r[ERR] {0}'.format(message), 'red', file=sys.stderr)
