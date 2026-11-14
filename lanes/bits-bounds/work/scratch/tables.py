"""Descriptive tables from the registered evaluation runs (medians over nets per configuration).
Post hoc in the sense that the table layout was chosen after PREREG; every number is a registered measurement.
Output: results/tables.md."""
import os
import json
import glob
import numpy as np

ROOT = os.path.join(os.path.dirname(__file__), '..')


def med(xs):
    xs = [x for x in xs if x is not None and np.isfinite(x)]
    return float(np.median(xs)) if xs else float('nan')


def main():
    nets = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'runs', 'eval_n*_L*_s*.json'))):
        r = json.load(open(f))
        if not r.get('dead'):
            nets.append(r)
    cfgs = sorted(set((r['n'], r['L']) for r in nets), key=lambda c: (c[1] / c[0], c[0]))
    lines = ['# Bits-bounds evaluation tables (medians over nets)', '']
    lines.append('## E1: cloud and merge residuals (forward-only references; D and bias in units of V_ang)')
    lines.append('')
    lines.append('| n x L (nets) | l | L\' | PR | ev slope | theta | meanprop | D_R(1) | D_F(1) | D_best(4) | D_best(16) | '
                 'D_best(64) | D_best(256) | bias_best(64) | bias_best(256) | D_best two-sided(64) | frac frozen (best, 64) |')
    lines.append('|' + '---|' * 17)
    for c in cfgs:
        rs = [r for r in nets if (r['n'], r['L']) == c]
        for li in range(len(rs[0]['E1'])):
            es = [r['E1'][li] for r in rs]
            row = [f'{c[0]}x{c[1]} ({len(rs)})', str(es[0]['l']), str(es[0]['Lp']),
                   '%.2f' % med([e['PR'] for e in es]), '%.2f' % med([e['ev_logslope_1_10'] for e in es]),
                   '%.3f' % med([e['theta_median'] for e in es]), '%.3g' % med([e['meanprop_err'] for e in es]),
                   '%.3g' % med([e['fwd']['1']['D_R'] for e in es]), '%.3g' % med([e['fwd']['1']['D_F'] for e in es])]
            for M in ['4', '16', '64', '256']:
                row.append('%.3g' % med([e['fwd'][M]['D_best'] for e in es]))
            for M in ['64', '256']:
                row.append('%.2g' % med([e['fwd'][M]['bias_best'] for e in es]))
            row.append('%.3g' % med([e['two']['64']['D_best'] if '64' in e['two'] else None for e in es]))
            row.append('%.2f' % med([e['fwd']['64']['frac_frozen_best'] for e in es]))
            lines.append('| ' + ' | '.join(row) + ' |')
    lines.append('')
    lines.append('## E1: bias against residual/M (the "references are samples" check): median of bias_best / (D_best/M)')
    lines.append('')
    lines.append('| n x L | l | M=4 | M=16 | M=64 | M=256 |')
    lines.append('|---|---|---|---|---|---|')
    for c in cfgs:
        rs = [r for r in nets if (r['n'], r['L']) == c]
        for li in range(len(rs[0]['E1'])):
            es = [r['E1'][li] for r in rs]
            row = [f'{c[0]}x{c[1]}', str(es[0]['l'])]
            for M in [4, 16, 64, 256]:
                row.append('%.2f' % med([e['fwd'][str(M)]['bias_best'] / max(e['fwd'][str(M)]['D_best'] / M, 1e-300)
                                         for e in es]))
            lines.append('| ' + ' | '.join(row) + ' |')
    lines.append('')
    lines.append('## E3: two-level samplers, ideal variance x cost relative to radius-exact MC (below 1 = gain)')
    lines.append('')
    lines.append('| n x L | r | random ref (radial) | M=1 radial | M=16 radial | M=64 radial | M=256 radial | M=64 rule | '
                 'M=256 rule | setup passes (M=256) |')
    lines.append('|' + '---|' * 10)
    for c in cfgs:
        rs = [r for r in nets if (r['n'], r['L']) == c]
        for ri in range(len(rs[0]['E3'])):
            es = [r['E3'][ri] for r in rs]
            row = [f'{c[0]}x{c[1]}', str(es[0]['r'])]
            for k in ['randref_R', 'M1_R', 'M16_R', 'M64_R', 'M256_R', 'M64_rule', 'M256_rule']:
                row.append('%.3f' % med([e[k]['ideal'] for e in es]))
            row.append('%.0f' % med([e['M256_R']['setup_passes'] for e in es]))
            lines.append('| ' + ' | '.join(row) + ' |')
    os.makedirs(os.path.join(ROOT, 'results'), exist_ok=True)
    open(os.path.join(ROOT, 'results', 'tables.md'), 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
