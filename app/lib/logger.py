import os
import sys

from termcolor import cprint


def debug(message):
    if 'DEBUG' in os.environ:
        cprint('\r[DBG] {0}'.format(message), 'blue', file=sys.stderr)


def info(message):
    cprint('\r[INF] {0}'.format(message), 'white', file=sys.stdout)


def warning(message):
    cprint('\r[WRN] {0}'.format(message), 'yellow', file=sys.stderr)


def error(message):
    cprint('\r[ERR] {0}'.format(message), 'red', file=sys.stderr)
