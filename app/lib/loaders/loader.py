"""
@AUTHOR: nuthanmunaiah
"""

from django.db import transaction


class Loader(object):
    """
    An abstract class containing stubs to be implemented.
    """
    def __init__(self, settings):
        """
        Constructor.
        """
        self.settings = settings

    def load(self):
        """
        Stub.
        """
        with transaction.atomic():
            return self._load()

    def _load(self):
        """
        Stub.
        """
        raise NotImplementedError()


