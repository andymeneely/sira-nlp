class Analyzer(object):
    def __init__(self, text):
        self.text = text

    def analyze(self):
        raise NotImplementedError()
