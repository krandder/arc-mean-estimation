"""Uc (descriptive): per layer position and mu, ReLU range (min / median / max over the 6 pairs) of the price and of
the pair's total rate change and total distortion change (nMSE / lambda), against the single tanh4 pair; and the share
of ReLU pairs below the tanh pair. lambda 0.01, affine S. usage: python3 scratch/report_Uc_sep.py [prefix] [lam] [smap]"""
import glob, json, sys
import numpy as np
W = '/home/agent/workspaces/mats/work/bit-accounting'
P, LAM, SM = (sys.argv + [None] * 4)[1:4]
P, LAM, SM = P or 'Uc', float(LAM or 0.01), SM or 'linear'
pos = lambda L, l: {0: 'input', L // 4: 'L/4', L // 2: 'L/2'}.get(l, '3L/4')  # noqa: E731
R = {}
for f in sorted(glob.glob(f'{W}/runs/U/{P}_*.json')):
    r = json.load(open(f))
    if r['lam'] != LAM or r['smap'] != SM:
        continue
    e, mus = r['end'], r['mus']; i0 = mus.index(0.0)
    for mi, mu in enumerate(mus):
        if mu == 0:
            continue
        dR = sum(e[f'rate_{j}'][mi] - e[f'rate_{j}'][i0] for j in range(2))
        dD = sum(e[f'nmse_{j}'][mi] - e[f'nmse_{j}'][i0] for j in range(2)) / LAM
        R.setdefault((pos(r['L'], r['l']), mu, r['kind']), []).append((dR + dD, dR, dD))
lines = [f'# {P}: ReLU (min / median / max over pairs) against tanh4, lambda {LAM}, S = {SM}; pair totals', '',
         '| layer | mu | price ReLU | price tanh4 | ReLU pairs below tanh4 | rate ReLU | rate tanh4 | dist ReLU | dist tanh4 |',
         '|' + '---|' * 9]
for p in ('input', 'L/4', 'L/2', '3L/4'):
    for mu in (0.1, 0.3, 1.0, 3.0):
        a = np.array(R.get((p, mu, 'relu'), [])); t = np.array(R.get((p, mu, 'tanh4'), []))
        if not len(a) or not len(t):
            continue
        rng = lambda c: f'{a[:, c].min():+.2f} / {np.median(a[:, c]):+.2f} / {a[:, c].max():+.2f}'  # noqa: E731
        lines.append(f'| {p} | {mu} | {rng(0)} | {t[0, 0]:+.2f} | {int((a[:, 0] < t[0, 0]).sum())}/{len(a)} | {rng(1)} | '
                     f'{t[0, 1]:+.2f} | {rng(2)} | {t[0, 2]:+.2f} |')
open(f'{W}/results/{P}_sep.md', 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
