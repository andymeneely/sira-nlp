import sys
from datetime import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand

from app.lib.helpers import *
from app.lib.logger import *
from app.models import *

URL = 'https://codereview.chromium.org/{review}/diff2/{psuno}:{psdos}/{path}'
URL2 = 'https://codereview.chromium.org/{review}/diff/{psuno}/{path}'


def show(text):
    sys.stdout.write('\r\033[K')
    sys.stdout.write('{}'.format(text))
    sys.stdout.flush()


class Command(BaseCommand):
    def handle(self, *args, **options):
        begin = dt.now()
        try:
            self.manual()
        except KeyboardInterrupt:  # pragma: no cover
            warning('Attempting to abort.')
        finally:
            info('Time: {:.2f} mins'.format(get_elapsed(begin, dt.now())))

    def manual(self):
        urls = list()
        for item in self.get_data():
            show(item)
            urls.append(self.get_columns(item))
        self.save_data(urls)

    def get_data(self):
        data = None
        with open('comments.csv') as file:
            reader = csv.reader(file)
            data = [int(row[0]) for row in reader]
        return data

    def get_columns(self, id):
        url = None
        comment = Comment.objects.get(id=id)
        path = comment.patch.file_path

        patchset = comment.patch.patchset
        patchsets = PatchSet.objects                              \
                            .filter(review=patchset.review)       \
                            .filter(files__contains=[path])       \
                            .filter(created__gt=patchset.created) \
                            .order_by('created')

        for patchset in patchsets:
            psdos = patchset.id
            url = URL.format(
                    review=patchset.review.id, path=path,
                    psuno=comment.patch.patchset.id, psdos=patchset.id
                )
            if url is not None:
                break
            else:
                url = URL2.format(
                        review=patchset.review.id, path=path,
                        psuno=comment.patch.patchset.id
                    )
                break

        retrn = (
                comment.patch.patchset.review.id,
                comment.patch.patchset.id,
                comment.patch.id,
                comment.id,
                comment.file_path,
                comment.line,
                comment.text[:25],
                'Yes' if comment.is_useful else 'No',
                '=HYPERLINK("{}", "View Diff")'.format(url)
            )
        return retrn

    def save_data(self, data):
        with open('comments.withurl.csv', 'w') as file:
            writer = csv.writer(file)
            writer.writerows(data)
