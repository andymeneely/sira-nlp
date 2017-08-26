import csv
import os

import cliffs_delta as cd

DATA_DIR = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        os.pardir, os.pardir, 'data', 'csv'
    )
LABELS = {
        'yngve': 'Yngve',
        'frazier': 'Frazier',
        'pdensity': 'p-density',
        'cdensity': 'c-density',
        'pct_neg_tokens': 'Negativity',
        'pct_neu_tokens': 'Neutrality',
        'pct_pos_tokens': 'Positivity',
        'pct_nne_tokens': 'Non-neutrality',
        'min_politeness': 'Min. Politeness',
        'max_politeness': 'Max. Politeness',
        'min_formality': 'Min. Formality',
        'max_formality': 'Max. Formality',
        'uni_prj_experience': 'Uniform Project Exp.',
        'prp_prj_experience': 'Proportional Project Exp.',
        'uni_mod_experience': 'Uniform Module Exp.',
        'prp_mod_experience': 'Proportional Module Exp.',
        'uni_fil_experience': 'Uniform File Exp.',
        'prp_fil_experience': 'Proportional File Exp.',
        'has_doxastic': 'Has Doxastic',
        'has_epistemic': 'Has Epistemic',
        'has_conditional': 'Has Conditional',
        'has_investigative': 'Has Investigative',
        # Sentence Uncertainty
        'yngve.is_doxastic': 'Yngve vs. Is Doxastic',
        'yngve.is_epistemic': 'Yngve vs. Is Epistemic',
        'yngve.is_conditional': 'Yngve vs. Is Conditional',
        'yngve.is_investigative': 'Yngve vs. Is Investigative',
        'yngve.is_uncertain': 'Yngve vs. Is Uncertain',
        'frazier.is_doxastic': 'Frazier vs. Is Doxastic',
        'frazier.is_epistemic': 'Frazier vs. Is Epistemic',
        'frazier.is_conditional': 'Frazier vs. Is Conditional',
        'frazier.is_investigative': 'Frazier vs. Is Investigative',
        'frazier.is_uncertain': 'Frazier vs. Is Uncertain',
        'pdensity.is_doxastic': 'Propositional Density vs. Is Doxastic',
        'pdensity.is_epistemic': 'Propositional Density vs. Is Epistemic',
        'pdensity.is_conditional': 'Propositional Density vs. Is Conditional',
        'pdensity.is_investigative': 'Propositional Density vs. Is Investigative',
        'pdensity.is_uncertain': 'Propositional Density vs. Is Uncertain',
        'cdensity.is_doxastic': 'Content Density vs. Is Doxastic',
        'cdensity.is_epistemic': 'Content Density vs. Is Epistemic',
        'cdensity.is_conditional': 'Content Density vs. Is Conditional',
        'cdensity.is_investigative': 'Content Density vs. Is Investigative',
        'cdensity.is_uncertain': 'Content Density vs. Is Uncertain',
        'politeness.is_doxastic': 'Politeness vs. Is Doxastic',
        'politeness.is_epistemic': 'Politeness vs. Is Epistemic',
        'politeness.is_conditional': 'Politeness vs. Is Conditional',
        'politeness.is_investigative': 'Politeness vs. Is Investigative',
        'politeness.is_uncertain': 'Politeness vs. Is Uncertain',
        'formality.is_doxastic': 'Formality vs. Is Doxastic',
        'formality.is_epistemic': 'Formality vs. Is Epistemic',
        'formality.is_conditional': 'Formality vs. Is Conditional',
        'formality.is_investigative': 'Formality vs. Is Investigative',
        'formality.is_uncertain': 'Formality vs. Is Uncertain',
        # Sentence Sentiment
        'yngve.is_positive': 'Yngve vs. Is Positive',
        'yngve.is_negative': 'Yngve vs. Is Negative',
        'frazier.is_positive': 'Frazier vs. Is Positive',
        'frazier.is_negative': 'Frazier vs. Is Negative',
        'pdensity.is_positive': 'Propositional Density vs. Is Positive',
        'pdensity.is_negative': 'Propositional Density vs. Is Negative',
        'cdensity.is_positive': 'Conditional Density vs. Is Positive',
        'cdensity.is_negative': 'Conditional Density vs. Is Negative',
        'politeness.is_positive': 'Politeness vs. Is Positive',
        'politeness.is_negative': 'Politeness vs. Is Negative',
        'formality.is_positive': 'Formality vs. Is Positive',
        'formality.is_negative': 'Formality vs. Is Negative',
    }
METRICS = {
        'comment': [
            'yngve',
            'frazier',
            'pdensity',
            'cdensity',
            'pct_neg_tokens',
            'pct_neu_tokens',
            'pct_pos_tokens',
            'pct_nne_tokens',
            'min_politeness',
            'max_politeness',
            'min_formality',
            'max_formality',
            'uni_prj_experience',
            'prp_prj_experience',
            'uni_mod_experience',
            'prp_mod_experience',
            'uni_fil_experience',
            'prp_fil_experience',
            'has_doxastic',
            'has_epistemic',
            'has_conditional',
            'has_investigative',
        ],
        'sentence': [
        # Sentence Sentiment
            'yngve.is_positive',
            'yngve.is_negative',
            'frazier.is_positive',
            'frazier.is_negative',
            'pdensity.is_positive',
            'pdensity.is_negative',
            'cdensity.is_positive',
            'cdensity.is_negative',
            'politeness.is_positive',
            'politeness.is_negative',
            'formality.is_positive',
            'formality.is_negative',
            # Sentence Uncertainty
            'yngve.is_doxastic',
            'yngve.is_epistemic',
            'yngve.is_conditional',
            'yngve.is_investigative',
            'yngve.is_uncertain',
            'frazier.is_doxastic',
            'frazier.is_epistemic',
            'frazier.is_conditional',
            'frazier.is_investigative',
            'frazier.is_uncertain',
            'pdensity.is_doxastic',
            'pdensity.is_epistemic',
            'pdensity.is_conditional',
            'pdensity.is_investigative',
            'pdensity.is_uncertain',
            'cdensity.is_doxastic',
            'cdensity.is_epistemic',
            'cdensity.is_conditional',
            'cdensity.is_investigative',
            'cdensity.is_uncertain',
            'politeness.is_doxastic',
            'politeness.is_epistemic',
            'politeness.is_conditional',
            'politeness.is_investigative',
            'politeness.is_uncertain',
            'formality.is_doxastic',
            'formality.is_epistemic',
            'formality.is_conditional',
            'formality.is_investigative',
            'formality.is_uncertain',
        ]
    }


def get_data(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath) as file:
        reader = csv.reader(file)
        return [row[0] for row in reader]


def get_distributions(granularity, metric):
    filename = '{}.{}.x.csv'.format(granularity, metric)
    x = get_data(os.path.join(DATA_DIR, filename))
    filename = '{}.{}.y.csv'.format(granularity, metric)
    y = get_data(os.path.join(DATA_DIR, filename))
    return (x, y)


def show_effect(granularities=['comment']):
    for granularity in granularities:
        print('  Granularity {}'.format(granularity))
        for metric in METRICS[granularity]:
            (x, y) = get_distributions(granularity, metric)
            if x and y:
                delta = cd.get_cliffsdelta(x, y)
                magnitude = cd.get_magnitude(delta)
                print('{:25} {:10.6f}({})'.format(
                        LABELS[metric], delta, magnitude
                    ))


if __name__ == '__main__':
    show_effect()
