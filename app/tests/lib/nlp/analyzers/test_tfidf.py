import os
import multiprocessing
import shutil
import tempfile

from django import test
from django.conf import settings

from app.lib.nlp import analyzers
from app.lib.utils import parallel


def generator(documents, inputq):
    for document in documents:
        inputq.put(document, block=True)


class TfIdfTestCase(test.TestCase):
    def start_generator(self):
        process = multiprocessing.Process(
                target=generator, args=(self.documents, self.tfidf.documents)
            )
        process.start()
        return process

    def setUp(self):
        self.documents = [
                (
                    'Google Chrome is a freeware web browser developed by Goog'
                    'le. It was first released in 2008, for Microsoft Windows,'
                    'and was later ported to Linux, macOS, watchOS, iOS and An'
                    'droid. Google Chrome is also the main component of Chrome'
                    ' OS, where it serves a platform for running web apps. Goo'
                    'gle releases the majority of Chrome\'s source code as the'
                    ' Chromium open-source project. A notable component that i'
                    's not open-source is the built-in Adobe Flash Player (tha'
                    't Chrome has disabled by default since September 2016). C'
                    'hrome used the WebKit layout engine until version 27. As '
                    'of version 28, all Chrome ports except the iOS port use B'
                    'link, a fork of the WebKit engine.'
                ),
                (
                    'Mozilla Firefox (or simply Firefox) is a free and open-so'
                    'urce web browser developed by the Mozilla Foundation and '
                    'its subsidiary, the Mozilla Corporation. Firefox is avail'
                    'able for Windows, macOS and Linux operating systems, with'
                    ' its Firefox for Android available for Android (formerly '
                    'Firefox for mobile, it also ran on the discontinued Firef'
                    'ox OS); where all of these versions use the Gecko layout '
                    'engine to render web pages, which implements current and '
                    'anticipated web standards. An additional version, Firefox'
                    ' for iOS, was released in late 2015, but this version doe'
                    'sn\'t use Gecko due to Apple\'s restrictions limiting thi'
                    'rd-party web browsers to the WebKit-based layout engine b'
                    'uilt into iOS.'
                ),
                (
                    'Opera is a web browser for Windows, macOS, and Linux oper'
                    'ating systems. It is developed by Opera Software. As of N'
                    'ovember 2016, the browser is owned by a Chinese group of '
                    'investors under the name Golden Brick Capital Private Equ'
                    'ity Fund I Limited Partnership. According to Opera Softwa'
                    're, the browser had more than 350 million users worldwide'
                    ' in the 4th quarter of 2014. Total Opera mobile users rea'
                    'ched 291 million in June 2015. According to SlashGeek, Op'
                    'era has originated features later adopted by other web br'
                    'owsers, including Speed Dial, pop-up blocking, browser se'
                    'ssions, private browsing, and tabbed browsing.'
                )
            ]
        self.tempdir = tempfile.mkdtemp()
        with self.settings(NLP_CACHE_PATH=self.tempdir, CPU_COUNT=3):
            self.tfidf = analyzers.TfIdf(settings, len(self.documents))
        self.document = self.documents[2]

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_initialize(self):
        self.assertFalse(self.tfidf.is_cached)
        process = self.start_generator()
        self.tfidf.initialize()
        process.join()
        self.assertTrue(self.tfidf.is_cached)
        self.tfidf.initialize()

    def test_get(self):
        expected = {
                ',': 0.0, '.': 0.0, '2014': 0.0096369, '2015': 0.0035567,
                '2016': 0.0035567, '291': 0.0096369, '350': 0.0096369,
                '4th': 0.0096369, 'a': 0.0, 'According': 0.0192739,
                'adopted': 0.0096369, 'and': 0.0, 'As': 0.0,
                'blocking': 0.0096369, 'Brick': 0.0096369, 'browser': 0.0,
                'browsers': 0.0, 'browsing': 0.0192739, 'by': 0.0,
                'Capital': 0.0096369, 'Chinese': 0.0096369, 'developed': 0.0,
                'Dial': 0.0096369, 'Equity': 0.0096369, 'features': 0.0,
                'for': 0.0, 'Fund': 0.0096369, 'Golden': 0.0096369,
                'group': 0.0096369, 'had': 0.0, 'has': 0.0, 'I': 0.0,
                'in': 0.0, 'including': 0.0096369, 'investors': 0.0, 'is': 0.0,
                'It': 0.0, 'June': 0.0096369, 'later': 0.0035567,
                'Limited': 0.0096369, 'Linux': 0.0, 'macOS': 0.0,
                'million': 0.0192739, 'mobile': 0.0035567, 'more': 0.0,
                'name': 0.0096369, 'November': 0.0096369, 'of': 0.0,
                'Opera': 0.0481847, 'operating': 0.0035567,
                'originated': 0.0096369, 'other': 0.0, 'owned': 0.0096369,
                'Partnership': 0.0096369, 'pop-up': 0.0096369,
                'private': 0.0096369, 'Private': 0.0096369,
                'quarter': 0.0096369, 'reached': 0.0096369, 'sessions': 0.0,
                'SlashGeek': 0.0096369, 'Software': 0.0192739,
                'Speed': 0.0096369, 'systems': 0.0, 'tabbed': 0.0096369,
                'than': 0.0, 'the': 0.0, 'to': 0.0, 'Total': 0.0096369,
                'under': 0.0, 'users': 0.0, 'web': 0.0, 'Windows': 0.0,
                'worldwide': 0.0096369
            }

        process = self.start_generator()
        self.tfidf.initialize()
        process.join()

        actual = self.tfidf.get(self.document)
        self.assertAlmostEqual(expected, actual)

        actual = self.tfidf.get(self.document, 'operating')
        self.assertAlmostEqual(expected['operating'], actual)

    def test_get_idf(self):
        expected = {
                '\'s': 0.4054651, '2008': 1.0986123, '2014': 1.0986123,
                '2015': 0.4054651, '2016': 0.4054651, '27': 1.0986123,
                '28': 1.0986123, '291': 1.0986123, '350': 1.0986123,
                '4th': 1.0986123, 'according': 1.0986123,
                'additional': 1.0986123, 'adobe': 1.0986123,
                'adopted': 1.0986123, 'also': 0.4054651, 'android': 0.4054651,
                'anticipated': 1.0986123, 'apple': 1.0986123,
                'apps': 1.0986123, 'available': 1.0986123, 'blink': 1.0986123,
                'blocking': 1.0986123, 'brick': 1.0986123, 'browser': 0.0,
                'browsing': 1.0986123, 'built': 1.0986123,
                'built-in': 1.0986123, 'capital': 1.0986123,
                'chinese': 1.0986123, 'chrome': 1.0986123,
                'chromium': 1.0986123, 'code': 1.0986123,
                'component': 1.0986123, 'corporation': 1.0986123,
                'current': 1.0986123, 'default': 1.0986123, 'developed': 0.0,
                'dial': 1.0986123, 'disabled': 1.0986123,
                'discontinued': 1.0986123, 'doe': 1.0986123, 'due': 1.0986123,
                'engine': 0.4054651, 'equity': 1.0986123, 'except': 1.0986123,
                'feature': 1.0986123, 'firefox': 1.0986123, 'first': 1.0986123,
                'flash': 1.0986123, 'fork': 1.0986123, 'formerly': 1.0986123,
                'foundation': 1.0986123, 'free': 1.0986123,
                'freeware': 1.0986123, 'fund': 1.0986123, 'gecko': 1.0986123,
                'golden': 1.0986123, 'google': 1.0986123, 'group': 1.0986123,
                'ha': 0.4054651, 'implement': 1.0986123,
                'including': 1.0986123, 'investor': 1.0986123,
                'ios': 0.4054651, 'june': 1.0986123, 'late': 1.0986123,
                'later': 0.4054651, 'layout': 0.4054651, 'limited': 1.0986123,
                'limiting': 1.0986123, 'linux': 0.0, 'macos': 0.0,
                'main': 1.0986123, 'majority': 1.0986123,
                'microsoft': 1.0986123, 'million': 1.0986123,
                'mobile': 0.4054651, 'mozilla': 1.0986123, 'n\'t': 1.0986123,
                'name': 1.0986123, 'notable': 1.0986123, 'november': 1.0986123,
                'open-source': 0.4054651, 'opera': 1.0986123,
                'operating': 0.4054651, 'originated': 1.0986123,
                'os': 0.4054651, 'owned': 1.0986123, 'page': 1.0986123,
                'partnership': 1.0986123, 'platform': 1.0986123,
                'player': 1.0986123, 'pop-up': 1.0986123, 'port': 1.0986123,
                'ported': 1.0986123, 'private': 1.0986123,
                'project': 1.0986123, 'quarter': 1.0986123, 'ran': 1.0986123,
                'reached': 1.0986123, 'release': 1.0986123,
                'released': 0.4054651, 'render': 1.0986123,
                'restriction': 1.0986123, 'running': 1.0986123,
                'september': 1.0986123, 'serf': 1.0986123,
                'session': 1.0986123, 'simply': 1.0986123, 'since': 1.0986123,
                'slashgeek': 1.0986123, 'software': 1.0986123,
                'source': 1.0986123, 'speed': 1.0986123, 'standard': 1.0986123,
                'subsidiary': 1.0986123, 'system': 0.4054651,
                'tabbed': 1.0986123, 'third-party': 1.0986123,
                'total': 1.0986123, 'use': 0.4054651, 'used': 1.0986123,
                'user': 1.0986123, 'version': 0.4054651, 'wa': 0.4054651,
                'watchos': 1.0986123, 'web': 0.0, 'webkit': 1.0986123,
                'webkit-based': 1.0986123, 'windows': 0.0,
                'worldwide': 1.0986123
            }

        with self.assertRaises(Exception):
            _ = self.tfidf.get_idf('')

        process = self.start_generator()
        self.tfidf.initialize()
        process.join()

        actual = self.tfidf.get_idf()
        self.assertAlmostEqual(expected, actual)

        actual = self.tfidf.get_idf('watchos')
        self.assertAlmostEqual(expected['watchos'], actual)

        actual = self.tfidf.get_idf('watchOS')
        self.assertAlmostEqual(expected['watchos'], actual)

    def test_get_tf(self):
        expected = {
                ',': 0.0877193, '.': 0.0526316, '2014': 0.0087719,
                '2015': 0.0087719, '2016': 0.0087719, '291': 0.0087719,
                '350': 0.0087719, '4th': 0.0087719, 'a': 0.0175439,
                'According': 0.0175439, 'adopted': 0.0087719, 'and': 0.0175439,
                'As': 0.0087719, 'blocking': 0.0087719, 'Brick': 0.0087719,
                'browser': 0.0350877, 'browsers': 0.0087719,
                'browsing': 0.0175439, 'by': 0.0263158, 'Capital': 0.0087719,
                'Chinese': 0.0087719, 'developed': 0.0087719,
                'Dial': 0.0087719, 'Equity': 0.0087719, 'features': 0.0087719,
                'for': 0.0087719, 'Fund': 0.0087719, 'Golden': 0.0087719,
                'group': 0.0087719, 'had': 0.0087719, 'has': .0087719,
                'I': 0.0087719, 'in': 0.0175439, 'including': 0.0087719,
                'investors': 0.0087719, 'is': 0.0263158, 'It': 0.0087719,
                'June': 0.0087719, 'later': 0.0087719, 'Limited': 0.0087719,
                'Linux': 0.0087719, 'macOS': 0.0087719, 'million': 0.0175439,
                'mobile': 0.0087719, 'more': 0.0087719, 'name': 0.0087719,
                'November': 0.0087719, 'of': 0.0263158, 'Opera': 0.0438596,
                'operating': 0.0087719, 'originated': 0.0087719,
                'other': 0.0087719, 'owned': 0.0087719,
                'Partnership': 0.0087719, 'pop-up': 0.0087719,
                'private': 0.0087719, 'Private': 0.0087719,
                'quarter': 0.0087719, 'reached': 0.0087719,
                'sessions': 0.0087719, 'SlashGeek': 0.0087719,
                'Software': 0.0175439, 'Speed': 0.0087719,
                'systems': 0.0087719, 'tabbed': 0.0087719, 'than': 0.0087719,
                'the': 0.0350877, 'to': 0.0175439, 'Total': 0.0087719,
                'under': 0.0087719, 'users': 0.0175439, 'web': 0.0175439,
                'Windows': 0.0087719, 'worldwide': 0.0087719
            }

        process = self.start_generator()
        self.tfidf.initialize()
        process.join()

        actual = self.tfidf.get_tf(self.document)
        self.maxDiff = None
        self.assertAlmostEqual(expected, actual)

        actual = self.tfidf.get_tf(self.document, 'operating')
        self.assertAlmostEqual(expected['operating'], actual)

    def assertAlmostEqual(self, first, second):
        _super = super(TfIdfTestCase, self)

        if not(type(first) is dict and type(second) is dict):
            _super.assertAlmostEqual(first, second)
        else:
            for key in first:
                _super.assertAlmostEqual(first[key], second[key])
