from django.db import transaction


class Tagger(object):
    def __init__(self, settings):
        self.settings = settings

    def tag(self):
        with transaction.atomic():
            return self._tag()

    def _tag(self):
        raise NotImplementedError()
