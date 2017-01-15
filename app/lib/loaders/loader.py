from django.db import transaction


class Loader(object):
    def __init__(self, settings):
        self.settings = settings

    def load(self):
        with transaction.atomic():
            return self._load()

    def _load(self):
        raise NotImplementedError()
