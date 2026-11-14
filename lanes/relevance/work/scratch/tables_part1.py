"""Accounting tables for the report from results/part1_scores.json and the raw runs (post-processing only).
Per cell: memory share, degree shares (s_1 Stein; s_2 upper estimate from the Mehler curve at rho = +-0.5:
s_2 + s_4/4 + ... = (2V - D(.5) - D(-.5)) / (0.5 V)), radial-direction share, mean degree, N (vector, scalar),
N_1 (registered: cumulative eigenvalues; unbiased: degree-1 captured by the AS basis via U-statistics), N_>=2 along the
AS basis, with v1 predictions. Writes results/part1_tables.md."""
import glob
import json
import sys

import numpy as np

sys.path.insert(0, '/home/agent/workspaces/mats/work/relevance/scratch')
import score_part1 as sp  # noqa: E402

BASE = '/home/agent/workspaces/mats/work/relevance/'


def n_from(curve_vals, V, eps):
    for k in sorted(curve_vals, key=int):
        if curve_vals[k] <= eps * V:
            return int(k)
    return None


def extra(o):
    V = o['V_gauss'][0]
    md = o['mehler_D']
    s2u = (2 * V - md['0.5'][0] - md['-0.5'][0]) / (0.5 * V)
    V1 = o['V1_gauss'][0]
    cap1 = o['cap1_AS']
    res = o['res_AS_gauss']
    r_nl = {k: res[k][0] - (V1 - cap1[k]) for k in res}
    r_1 = {k: (V1 - cap1[k]) for k in res}
    return dict(s2u=s2u, rad_share=1 - o['res_radial_gauss'][0] / V,
                N1u={e: n_from(r_1, V1, e) for e in (0.1, 0.01)},
                Nnl={e: n_from(r_nl, V, e) for e in (0.1, 0.01, 0.001)})


def fmtN(meas, pred):
    return f"{meas[1]}/{pred}"


def main():
    sc = json.load(open(BASE + 'results/part1_scores.json'))
    lines = ['# Part 1 accounting tables (measured / theory v1)', '',
             'N columns: measured upper bound on the AS-basis grid / v1 prediction. N1: registered (cumulative '
             'eigenvalues, biased low by sampling noise) | unbiased (U-statistic on the AS basis) | free-product '
             'prediction. N>=2: degree >= 2 residual along the AS basis (for the mean). s2u = s_2 + s_4/4 + ...', '']
    raws = {}
    for fn in sorted(glob.glob(BASE + 'runs/eval_*.json')):
        for o in json.load(open(fn)):
            key = (o['mode'], o['n'], o['seed'], o.get('l'), o.get('s'))
            raws[key] = o
    hdr = ('| regime | n | seed | l or s | t | M | s1 meas/v1 | s2u | radial share | D meas/v1 | N(.1) | N(.01) | N(.001) | '
           'Nsc(.1) | Nsc(.01) | N1(.01) reg/unb/fp | N>=2 (.1, .01, .001) |')
    lines += [hdr, '|' + '---|' * 17]
    for c in sc['cells']:
        o = raws[(c['mode'], c['n'], c['seed'], c['l'], c['s'])]
        ex = extra(o)
        lab = c['l'] if c['l'] is not None else c['s']
        M = f"{c.get('M', 1.0):.3f}"
        flag = '' if c['resolved'] else ' (unres.)'
        p = lambda k: c.get(k, '-')
        lines.append(f"| {c['mode']}{flag} | {c['n']} | {c['seed']} | {lab} | {c['t']} | {M} | "
                     f"{c['s1']:.3f}/{p('pred_s1') if isinstance(p('pred_s1'), str) else round(p('pred_s1'), 3)} | "
                     f"{ex['s2u']:.3f} | {ex['rad_share']:.3f} | {c['D']:.2f}/"
                     f"{p('pred_D') if isinstance(p('pred_D'), str) else round(p('pred_D'), 2)} | "
                     f"{fmtN(c['Nvec_0.1'], p('pred_Nvec_0.1'))} | {fmtN(c['Nvec_0.01'], p('pred_Nvec_0.01'))} | "
                     f"{fmtN(c['Nvec_0.001'], p('pred_Nvec_0.001'))} | {fmtN(c['Nsc_0.1'], p('pred_Nsc_0.1'))} | "
                     f"{fmtN(c['Nsc_0.01'], p('pred_Nsc_0.01'))} | {c['N1_0.01']}/{ex['N1u'][0.01]}/{p('pred_N1_0.01')} | "
                     f"{ex['Nnl'][0.1]}, {ex['Nnl'][0.01]}, {ex['Nnl'][0.001]} |")
    lines += ['', '## Scores', '']
    for k, v in sc['scores'].items():
        lines.append(f'- {k}: {v}')
    open(BASE + 'results/part1_tables.md', 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines[:60]))


if __name__ == '__main__':
    main()
