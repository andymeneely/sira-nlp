from unittest import TestCase

from json import JSONDecodeError

from app.lib.nlp import analyzers


class SentenceParseAnalyzerTestCase(TestCase):
    def setUp(self):
        pass

    def test_analyze(self):
        # Sub-Test 1
        data = ( '' )
        expected = {'deps': [], 'trees': []}
        actual = analyzers.SentenceParseAnalyzer(data).analyze()
        self.assertDictEqual(expected, actual)

        # Sub-Test 2
        data = (
                'Gulf Applied Technologies Inc said it sold its subsidiaries '
                'engaged in pipeline and terminal operations for 12.2 mln '
                'dlrs. '
            )

        expected = {
               'trees':
                   '(ROOT\n  (S\n    (NP (NNP Gulf) (NNP Applied) (NNPS Techno' \
                   'logies) (NNP Inc))\n    (VP (VBD said)\n      (SBAR\n     ' \
                   '   (S\n          (NP (PRP it))\n          (VP (VBD sold)\n' \
                   '            (NP\n              (NP (PRP$ its) (NNS subsidi' \
                   'aries))\n              (VP (VBN engaged)\n                ' \
                   '(PP (IN in)\n                  (NP\n                    (N' \
                   'P (NN pipeline))\n                    (CC and)\n          ' \
                   '          (NP (JJ terminal) (NNS operations))))\n         ' \
                   '       (PP (IN for)\n                  (NP (CD 12.2) (CD m' \
                   'ln) (NNS dlrs)))))))))\n    (. .)))',
               'deps': [
                    {
                        'dep': 'ROOT', 'governorGloss': 'ROOT',
                        'dependentGloss': 'said', 'governor': 0, 'dependent': 5
                    },
                    {
                        'dep': 'compound', 'governorGloss': 'Inc',
                        'dependentGloss': 'Gulf', 'governor': 4, 'dependent': 1
                    },
                    {
                        'dep': 'compound', 'governorGloss': 'Inc',
                        'dependentGloss': 'Applied', 'governor': 4,
                        'dependent': 2
                    },
                    {
                        'dep': 'compound', 'governorGloss': 'Inc',
                        'dependentGloss': 'Technologies', 'governor': 4,
                        'dependent': 3
                    },
                    {
                        'dep': 'nsubj', 'governorGloss': 'said',
                        'dependentGloss': 'Inc', 'governor': 5, 'dependent': 4
                    },
                    {
                        'dep': 'nsubj', 'governorGloss': 'sold',
                        'dependentGloss': 'it', 'governor': 7, 'dependent': 6
                    },
                    {
                        'dep': 'ccomp', 'governorGloss': 'said',
                        'dependentGloss': 'sold', 'governor': 5, 'dependent': 7
                    },
                    {
                        'dep': 'nmod:poss', 'governorGloss': 'subsidiaries',
                        'dependentGloss': 'its', 'governor': 9, 'dependent': 8
                    },
                    {
                        'dep': 'dobj', 'governorGloss': 'sold',
                        'dependentGloss': 'subsidiaries', 'governor': 7,
                        'dependent': 9
                    },
                    {
                        'dep': 'acl', 'governorGloss': 'subsidiaries',
                        'dependentGloss': 'engaged', 'governor': 9,
                        'dependent': 10
                    },
                    {
                        'dep': 'case', 'governorGloss': 'pipeline',
                        'dependentGloss': 'in', 'governor': 12, 'dependent': 11
                    },
                    {
                        'dep': 'nmod:in', 'governorGloss': 'engaged',
                        'dependentGloss': 'pipeline', 'governor': 10,
                        'dependent': 12
                    },
                    {
                        'dep': 'cc', 'governorGloss': 'pipeline',
                        'dependentGloss': 'and', 'governor': 12, 'dependent': 13
                    },
                    {
                        'dep': 'amod', 'governorGloss': 'operations',
                        'dependentGloss': 'terminal', 'governor': 15,
                        'dependent': 14
                    },
                    {
                        'dep': 'nmod:in', 'governorGloss': 'engaged',
                        'dependentGloss': 'operations', 'governor': 10,
                        'dependent': 15
                    },
                    {
                        'dep': 'conj:and', 'governorGloss': 'pipeline',
                        'dependentGloss': 'operations', 'governor': 12,
                        'dependent': 15
                    },
                    {
                        'dep': 'case', 'governorGloss': 'dlrs',
                        'dependentGloss': 'for', 'governor': 19, 'dependent': 16
                    },
                    {
                        'dep': 'compound', 'governorGloss': 'mln',
                        'dependentGloss': '12.2', 'governor': 18, 'dependent': 17
                    },
                    {
                        'dep': 'nummod', 'governorGloss': 'dlrs',
                        'dependentGloss': 'mln', 'governor': 19, 'dependent': 18
                    },
                    {
                        'dep': 'nmod:for', 'governorGloss': 'sold',
                        'dependentGloss': 'dlrs', 'governor': 7, 'dependent': 19
                    },
                    {
                        'dep': 'punct', 'governorGloss': 'said',
                        'dependentGloss': '.', 'governor': 5, 'dependent': 20
                    }
                ]
            }
        actual = analyzers.SentenceParseAnalyzer(data).analyze()
        self.assertEqual(expected['trees'], actual['trees'])
        self.assertListEqual(expected['deps'], actual['deps'])

    def test_failing(self):
        data = {
                "This roll was created by the Blink AutoRollBot.": ""
            }

        for k, v in data.items():
            actual = analyzers.SentenceParseAnalyzer(k).analyze()
            print(actual)
