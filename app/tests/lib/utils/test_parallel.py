import multiprocessing
import time

from unittest import TestCase

from app.lib.utils import parallel


def aggregate_with_return(oqueue, cqueue, num_doers):
    done = 0
    while True:
        item = cqueue.get()
        if item == parallel.DD:
            done += 1
            if done == num_doers:
                break
            continue
        oqueue.put(item + 10)


def aggregate_without_return(oqueue, cqueue, num_doers):
    done = 0
    while True:
        item = cqueue.get()
        if item == parallel.DD:
            done += 1
            if done == num_doers:
                break
            continue


def do(iqueue, cqueue):
    while True:
        item = iqueue.get()
        if item == parallel.EOI:
            cqueue.put(parallel.DD)
            break
        cqueue.put(item)


def stream(items, iqueue, num_doers):
    for item in items:
        iqueue.put(item)

    for i in range(num_doers):
        iqueue.put(parallel.EOI)


class ParallelTestCase(TestCase):
    def setUp(self):
        self.count = 100

    def test_run_with_return(self):
        iqueue = parallel.manager.Queue()

        process = multiprocessing.Process(
                target=stream, args=(list(range(self.count)), iqueue, 2)
            )
        process.start()

        expected = [(i + 10) for i in range(self.count)]
        aggregate = aggregate_with_return
        actual = parallel.run(do, aggregate, iqueue, 2)
        self.assertCountEqual(expected, actual)

        process.join()

    def test_run_without_return(self):
        iqueue = parallel.manager.Queue()

        process = multiprocessing.Process(
                target=stream, args=(list(range(self.count)), iqueue, 2)
            )
        process.start()

        expected = [(i + 10) for i in range(self.count)]
        aggregate = aggregate_without_return
        actual = parallel.run(do, aggregate, iqueue, 2)
        self.assertIsNone(actual)

        process.join()
