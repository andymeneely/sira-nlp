from datetime import datetime

from app.lib import files
from app.models import *
from app.lib.loaders import loader


class BugLoader(loader.Loader):
    def __init__(self, settings):
        super(BugLoader, self).__init__(settings)

    def _load(self):
        count = 0

        f = files.Files(self.settings)
        for year in self.settings.YEARS:
            for bug in f.get_bugs(year):
                b = Bug()

                b.id = bug['id']
                b.type = bug['type']
                b.status = bug['status']
                b.opened = datetime.strptime(
                        bug['opened'], '%b %d, %Y %H:%M:%S'
                    )
                b.document = bug
                if bug['cve'] != '':
                    for cve in bug['cve'].split(','):
                        v = Vulnerability(cve='CVE-{}'.format(cve.strip()))
                        b.vulnerability_set.add(v, bulk=False)

                b.save()
                count += 1

        return count
