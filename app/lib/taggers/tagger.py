"""
@AUTHOR: nuthanmunaiah
"""

from django.db import transaction


class Tagger(object):
    """
    Abstract class with function stubs to be implemented.
    """
    def __init__(self, settings, num_processes):
        """
        Constructor.
        """
        self.settings = settings
        self.num_processes = num_processes

    def tag(self):
        """
        Stub.
        """
        with transaction.atomic():
            return self._tag()

    def _tag(self):
        """
        Stub.
        """
        raise NotImplementedError()
