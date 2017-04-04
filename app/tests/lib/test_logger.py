"""
@AUTHOR: meyersbs
"""

from unittest import TestCase

from app.lib import logger


class LoggerTestCase(TestCase):
    """

    """
    def setUp(self):
        self.logger = logger
        pass

    def test_debug(self):
        expected = "This is a test log for '[DBG]'."
        self.logger.debug("This is a test log for '[DBG]'.")
        actual = self.logger.get_last_log()

        self.assertEqual(expected, actual)

    def test_info(self):
        expected = "This is a test log for '[INF]'."
        self.logger.info("This is a test log for '[INF]'.")
        actual = self.logger.get_last_log()

        self.assertEqual(expected, actual)

    def test_warning(self):
        expected = "This is a test log for '[WRN]'."
        self.logger.warning("This is a test log for '[WRN]'.")
        actual = self.logger.get_last_log()

        self.assertEqual(expected, actual)

    def test_error(self):
        expected = "This is a test log for '[ERR]'."
        self.logger.error("This is a test log for '[ERR]'.")
        actual = self.logger.get_last_log()

        self.assertEqual(expected, actual)
