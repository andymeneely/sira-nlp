"""
@AUTHOR: nuthanmunaiah
"""

import multiprocessing
import contextlib

from multiprocessing import Manager, Pool, Process

from app.lib import helpers

manager = Manager()
EOI = 'ENDOFINPUT'
DD = 'DOERDONE'


def run(doer, aggregator, iqueue, num_doers):
    '''
    Run a pool of doers and an aggregator.

    Parameters
    ----------
    doer: function
        Reference to a function that has the signature doer(iqueue, cqueue)
        where iqueue and cqueue are multiprocessing.Manager managed queues with
        iqueue used to stream input to the doer and cqueue is used by the doer
        to stream intermediate output to the aggregator.
    aggregator: function
        Reference to a function that has the signature
        aggregator(oqueue, cqueue) where oqueue and cqueue are
        multiprocessing.Manager managed queues with oqueue used to communicate
        output to this function (i.e. run) and cqueue is used to receive a
        stream of intermediate output (if any) from the doers.
    iqueue: multiprocessing.Queue
        Queue that is used to strem input to the doers.
    num_inputs: int
        Number of inputs to expect to be streamed. The parameter is used when
        creating the pool of doers.
    num_doers: int
        Number of doers (processes) to spawn.

    Returns
    -------
    return_: Multiple Types
        The return value and its type depend on the contents of the queue used
        by the aggregator to stream output. If the queue has multiple values, a
        list containing the contents of the queue is returned. If the queue has
        a single value, the single value is returned. If the queue is empty,
        None is returned.
    '''
    # Queues for communication and output
    cqueue = manager.Queue(maxsize=5000)
    oqueue = manager.Queue()

    # Aggregator Process
    process = Process(target=aggregator, args=(oqueue, cqueue, num_doers))
    process.start()

    # Doer Processe(s)
    with Pool(num_doers) as pool:
        pool.starmap(doer, [(iqueue, cqueue) for i in range(num_doers)], 1)

    process.join()

    return_ = None
    if not oqueue.empty():
        return_ = helpers.to_list(oqueue)
        return_ = return_[0] if len(return_) == 1 else return_
    return return_
