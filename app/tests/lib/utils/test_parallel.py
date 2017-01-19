import multiprocessing
from unittest import TestCase

from app.lib.utils import parallel

CPU_COUNT = multiprocessing.cpu_count()


def produce(inputq, commq):
    item = inputq.get(block=True)
    commq.put(item, block=True)


def consume(outputq, commq):
    while True:
        item = commq.get(block=True)
        if item == parallel.END:
            break
        outputq.put(item + 10, block=True)


def generator(items, inputq):
    for item in items:
        inputq.put(item, block=True)


class ParallelTestCase(TestCase):
    def setUp(self):
        self.count = 100

    def test_run(self):
        inputq = parallel.manager.Queue()

        process = multiprocessing.Process(
                target=generator, args=(list(range(0, self.count)), inputq)
            )
        process.start()

        expected = [(i + 10) for i in range(0, self.count)]
        actual = parallel.run(produce, consume, inputq, self.count, CPU_COUNT)
        self.assertCountEqual(expected, actual)

        process.join()
