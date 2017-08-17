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
        'prp_fil_experience': 'Proportional File Exp.'
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
            'prp_fil_experience'
        ]
    }


def get_data(filepath):
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
            delta = cd.get_cliffsdelta(x, y)
            magnitude = cd.get_magnitude(delta)
            print('{:25} {:10.6f}({})'.format(
                    LABELS[metric], delta, magnitude
                ))


if __name__ == '__main__':
    show_effect()
