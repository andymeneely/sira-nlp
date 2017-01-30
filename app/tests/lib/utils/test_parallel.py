import multiprocessing
import time

from unittest import TestCase

from app.lib.utils import parallel


def aggregate_with_return(oqueue, cqueue):
    while True:
        item = cqueue.get()
        if item == parallel.END:
            break
        oqueue.put(item + 10)


def aggregate_without_return(oqueue, cqueue):
    while True:
        item = cqueue.get()
        if item == parallel.END:
            break


def do(iqueue, cqueue):
    item = iqueue.get()
    cqueue.put(item)


def stream(items, iqueue):
    for item in items:
        iqueue.put(item)


class ParallelTestCase(TestCase):
    def setUp(self):
        self.count = 100

    def test_run_with_return(self):
        iqueue = parallel.manager.Queue()

        process = multiprocessing.Process(
                target=stream, args=(list(range(0, self.count)), iqueue)
            )
        process.start()

        expected = [(i + 10) for i in range(0, self.count)]
        aggregate = aggregate_with_return
        actual = parallel.run(do, aggregate, iqueue, self.count, 2)
        self.assertCountEqual(expected, actual)

        process.join()

    def test_run_without_return(self):
        iqueue = parallel.manager.Queue()

        process = multiprocessing.Process(
                target=stream, args=(list(range(0, self.count)), iqueue)
            )
        process.start()

        expected = [(i + 10) for i in range(0, self.count)]
        aggregate = aggregate_without_return
        actual = parallel.run(do, aggregate, iqueue, self.count, 2)
        self.assertIsNone(actual)

        process.join()
