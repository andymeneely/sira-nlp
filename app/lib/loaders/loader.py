"""
@AUTHOR: nuthanmunaiah
"""

from django.db import transaction


class Loader(object):
    """
    An abstract class containing stubs to be implemented.
    """
    def __init__(self, settings, num_processes):
        """
        Constructor.
        """
        self.settings = settings
        self.num_processes = num_processes

    def load(self):
        """
        Stub.
        """
        raise NotImplementedError()
