"""
@AUTHOR: nuthanmunaiah
"""

from app.lib import files, helpers
from app.lib.loaders import loader
from app.models import *


class ReviewLoader(loader.Loader):
    """
    Implements loader object.
    """
    def _load(self):
        """
        Grabs all of the reviews created within the specified range of years,
        parses them, cleans them up, and saves them. Returns the total number
        of loaded reviews.
        """
        count = 0

        f = files.Files(self.settings)
        for year in self.settings.YEARS:
            for review in f.get_reviews(year):
                r = Review()

                r.id = review['issue']
                r.created = review['created']
                r.is_open = True if not review['closed'] else False
                r.num_messages = len(review['messages'])
                r.document = f.transform_review(review)
                for id in helpers.parse_bugids(review['description']):
                    b = helpers.get_row(Bug, id=id)
                    if b is not None:
                        rb = ReviewBug(review=r, bug=b)
                        rb.save()

                r.save()
                count += 1

        return count
