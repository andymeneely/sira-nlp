"""
@AUTHOR: nuthanmunaiah
"""
import multiprocessing
import sys
import traceback

from datetime import datetime

from django.db import Error, transaction

from app.lib import files, helpers, loaders
from app.lib.utils import parallel
from app.models import *


def aggregate(oqueue, cqueue, num_doers):
    count, done = 0, 0
    while True:
        item = cqueue.get()
        if item == parallel.DD:
            done += 1
            if done == num_doers:
                break  # All doers are done
            continue  # pragma: no cover

        (bug, cves) = item
        try:
            with transaction.atomic():
                bug.save()
                objects = list()
                for cve in cves:
                    vulnerability = helpers.get_row(Vulnerability, id=cve)
                    if vulnerability is None:
                        vulnerability = Vulnerability(id=cve)
                        vulnerability.save()

                    objects.append(VulnerabilityBug(
                            vulnerability=vulnerability, bug=bug
                        ))
                if objects:
                    VulnerabilityBug.objects.bulk_create(objects)
                count += 1
        except Error as err:  # pragma: no cover
            sys.stderr.write('Exception\n')
            sys.stderr.write('  Bug  {}\n'.format(bug.id))
            extype, exvalue, extrace = sys.exc_info()
            traceback.print_exception(extype, exvalue, extrace)

    oqueue.put(count)


def do(iqueue, cqueue):  # pragma: no cover
    while True:
        item = iqueue.get()
        if item == parallel.EOI:
            cqueue.put(parallel.DD)
            break

        type, cves = '', list()
        if 'labels' in item:
            for label in item['labels']:
                if label.startswith('Type-'):
                    type = label.replace('Type-', '')
                if label.startswith('CVE-'):
                    cves.append(label)

        bug = Bug(
                id=item['id'], type=type, status=item['status'], document=item
            )
        cqueue.put((bug, cves))


def stream(iqueue, settings, num_doers):
    f = files.Files(settings)
    for year in settings.YEARS:
        for bug in f.get_bugs(year):
            iqueue.put(f.transform_bug(bug))

    for i in range(num_doers):
        iqueue.put(parallel.EOI)


class BugLoader(loaders.Loader):
    """
    Implements loader object.
    """
    def load(self):
        """
        Grabs all of the bugs from within the specified range of years,
        parses through them, cleans them up, then saves them. Returns the
        total number of bugs loaded.
        """
        count = 0

        iqueue = parallel.manager.Queue(self.settings.QUEUE_SIZE)
        process = self._start_streaming(iqueue)
        count = parallel.run(do, aggregate, iqueue, self.num_processes)
        process.join()

        return count

    def _start_streaming(self, iqueue):
        process = multiprocessing.Process(
                target=stream, args=(iqueue, self.settings, self.num_processes)
            )
        process.start()
        return process
