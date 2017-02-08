"""
@AUTHOR: nuthanmunaiah
"""

from datetime import datetime

from app.lib import files, helpers
from app.models import *
from app.lib.loaders import loader


class BugLoader(loader.Loader):
    """
    Implements loader object.
    """
    def __init__(self, settings):
        """
        Constructor.
        """
        super(BugLoader, self).__init__(settings)

    def _load(self):
        """
        Grabs all of the bugs from within the specified range of years,
        parses through them, cleans them up, then saves them. Returns the
        total number of bugs loaded.
        """
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
                        v = helpers.get_row(Vulnerability, id=cve)
                        if v is None:
                            v = Vulnerability(id='CVE-{}'.format(cve.strip()))
                            v.save()
                        vb = VulnerabilityBug(vulnerability=v, bug=b)
                        vb.save()
                b.save()
                count += 1

        return count
