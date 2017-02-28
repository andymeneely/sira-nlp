from unittest import TestCase

from app.lib.nlp import tokenremover


class StopWordsRemoverTestCase(TestCase):
    def setUp(self):
        pass

    def test_execute(self):
        # Exception
        data = []
        with self.assertRaises(Exception, msg='ZZ is an unknown filter'):
            _ = tokenremover.TokenRemover(data, filters=['ZZ'])

        # Stop Words Removal
        data = [
                'Gulf', 'Applied', 'Technologies', 'Inc', 'said', 'it', 'sold',
                'its', 'subsidiaries', 'engaged', 'in', 'pipeline', 'and',
                'terminal', 'operations', 'for', '12.2', 'mln', 'dlrs', '.',
                'The', 'company', 'said', 'the', 'sale', 'is', 'subject', 'to',
                'certain', 'post', 'closing', 'adjustments', ',', 'which',
                'it', 'did', 'not', 'explain', '.', 'Reuter'
            ]
        expected = [
                'Gulf', 'Applied', 'Technologies', 'Inc', 'said', 'sold',
                'subsidiaries', 'engaged', 'pipeline', 'terminal',
                'operations', '12.2', 'mln', 'dlrs', '.', 'company',
                'said', 'sale', 'subject', 'certain', 'post', 'closing',
                'adjustments', ',', 'explain', '.', 'Reuter'
            ]
        actual = tokenremover.TokenRemover(data, filters=['SW']).execute()
        self.assertEqual(expected, actual, msg='Stop words.')

        data = [
                'Stop', 'word', 'removal', 'MUST', 'BE', 'case-insensitive',
                '.'
            ]
        expected = ['Stop', 'word', 'removal', 'MUST', 'case-insensitive', '.']
        actual = tokenremover.TokenRemover(data, filters=['SW']).execute()
        self.assertEqual(expected, actual, msg='Stop words case insentivity.')

        # Punctuation Removal
        data = [
                'Gulf', 'Applied', 'Technologies', 'Inc', 'said', 'it', 'sold',
                'its', 'subsidiaries', 'engaged', 'in', 'pipeline', 'and',
                'terminal', 'operations', 'for', '12.2', 'mln', 'dlrs', '.',
                'The', 'company', 'said', 'the', 'sale', 'is', 'subject', 'to',
                'certain', 'post', 'closing', 'adjustments', ',', 'which',
                'it', 'did', 'not', 'explain', '.', 'Reuter'
            ]
        expected = [
                'Gulf', 'Applied', 'Technologies', 'Inc', 'said', 'it', 'sold',
                'its', 'subsidiaries', 'engaged', 'in', 'pipeline', 'and',
                'terminal', 'operations', 'for', '12.2', 'mln', 'dlrs', 'The',
                'company', 'said', 'the', 'sale', 'is', 'subject', 'to',
                'certain', 'post', 'closing', 'adjustments', 'which', 'it',
                'did', 'not', 'explain', 'Reuter'
            ]

        actual = tokenremover.TokenRemover(data, filters=['PU']).execute()
        self.assertEqual(expected, actual, msg='Punctuation')

        # Numbers Removal
        data = [
                '-8', '8', '+0000', '-07000', '7.1', '-0.0', '2010.6', '-10',
                '-1.', '9.', '.0', '.', '+', '-'
            ]
        expected = ['.', '+', '-']

        actual = tokenremover.TokenRemover(data, filters=['NU']).execute()
        self.assertEqual(expected, actual, msg='Numbers')

        # Word Length Based Removal
        data = [
                'chromium/src/third_party/icu/source/common/unicode/locid.h',
                '../../android_webview/browser/aw_content_browser_client.cc',
                '214a8cbf96c1dc8b2f7770bdeaaed978b09c6363', 'retain'
            ]
        expected = ['retain']

        actual = tokenremover.TokenRemover(data, filters=['WL']).execute()
        self.assertEqual(expected, actual, msg='Word length.')

        # Word Length Based Removal (Length Configuration)
        data = [
                'retain', 'looks-good-to-me', 'characteristically',
                'supercalifragilisticexpealidoshus', 'technologically',
                'uninterpenetratingly'
            ]
        expected = [
                'retain', 'looks-good-to-me', 'characteristically',
                'technologically'
            ]

        actual = tokenremover.TokenRemover(
                data, filters=['WL'], configuration={'WL': {'length': 20}}
            ).execute()
        self.assertEqual(expected, actual, msg='Word length.')

        # Special Characters Removal
        data = [
                'should-be-removed', 'should_not_be_removed'
            ]
        expected = ['should_not_be_removed']

        actual = tokenremover.TokenRemover(data, filters=['SC']).execute()
        self.assertEqual(expected, actual, msg='Special characters.')

        # All
        data = [
                'And', 'but', 'this', 'that', ',', ';', '"', "'", '+', '-',
                '+0000', '-07000', '7.1', '-0.0', '2010.6', '-10', '20334.'
                'chromium/src/third_party/icu/source/common/unicode/locid.h',
                '214a8cbf96c1dc8b2f7770bdeaaed978b09c6363',
                'bug', 'security', 'arbitrary', 'ladiesman217'
            ]
        expected = ['bug', 'security', 'arbitrary', 'ladiesman217']

        actual = tokenremover.TokenRemover(data).execute()
        self.assertEqual(expected, actual, msg='All')
