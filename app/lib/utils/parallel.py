import multiprocessing

from app.lib import helpers

manager = multiprocessing.Manager()
END = 'ENDCOMMUNICATION'


def run(produce, consume, inputq, num_inputs, num_processes):
    # Queues for communication and output
    commq = manager.Queue()
    outputq = manager.Queue()

    # Consumer Process
    process = multiprocessing.Process(target=consume, args=(outputq, commq))
    process.start()

    # Producer Processe(s)
    with multiprocessing.Pool(num_processes) as pool:
        pool.starmap(produce, [(inputq, commq) for i in range(0, num_inputs)])
        commq.put(END, block=True)

    process.join()

    retrn = helpers.to_list(outputq)
    return retrn if len(retrn) > 1 else retrn[0]
