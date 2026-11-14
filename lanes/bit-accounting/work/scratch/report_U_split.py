"""Part U, descriptive split (not a registered score): per kind, layer position and mu, the change against mu = 0 of
the rate (bits) and of the distortion term (nMSE / lambda, in bit units) for each layer of the pair (this = layer l,
next = layer l+1), plus their sum (= the price of report_U.py), and
(amendment U-c) the rate change of the pair where both layers' nMSE moves by < 5%. Medians over seeds/pairs, lambda 0.01, affine S.
usage: python3 scratch/report_U_split.py [prefix, default U] [lam] [smap] -> stdout and results/<prefix>_split.md"""
import glob
import json
import sys

import numpy as np

W = '/home/agent/workspaces/mats/work/bit-accounting'
P = sys.argv[1] if len(sys.argv) > 1 else 'U'
LAM = float(sys.argv[2]) if len(sys.argv) > 2 else 0.01
SMAP = sys.argv[3] if len(sys.argv) > 3 else 'linear'
U = [json.load(open(f)) for f in sorted(glob.glob(f'{W}/runs/U/{P}_*.json'))]
U = [r for r in U if r['lam'] == LAM and r['smap'] == SMAP]


def pos(L, l):
    return {0: 'input', L // 4: 'L/4', L // 2: 'L/2'}.get(l, '3L/4')


rows = {}
for r in U:
    e, mus = r['end'], r['mus']
    i0 = mus.index(0.0)
    for mi, mu in enumerate(mus):
        if mu == 0.0:
            continue
        d = {}
        for j, nm in ((0, 'this'), (1, 'next')):
            d[f'dR_{nm}'] = e[f'rate_{j}'][mi] - e[f'rate_{j}'][i0]
            d[f'dD_{nm}'] = (e[f'nmse_{j}'][mi] - e[f'nmse_{j}'][i0]) / LAM
            d[f'R0_{nm}'] = e[f'rate_{j}'][i0]
        d['price'] = d['dR_this'] + d['dD_this'] + d['dR_next'] + d['dD_next']
        # amendment U-c: extra bits at matched distortion only where both layers' nMSE moves by < 5% (relative)
        okd = all(abs(e[f'nmse_{j}'][mi] / max(e[f'nmse_{j}'][i0], 1e-12) - 1.0) < 0.05 for j in range(2))
        d['matched'] = (d['dR_this'] + d['dR_next']) if okd else None
        rows.setdefault((r['kind'], pos(r['L'], r['l']), mu), []).append(d)
        rows.setdefault((r['kind'], 'all', mu), []).append(d)
        if r['l'] > 0:
            rows.setdefault((r['kind'], 'L/4 on', mu), []).append(d)
order = ['all', 'L/4 on', 'input', 'L/4', 'L/2', '3L/4']
f = lambda xs: f'{np.median(xs):+.2f}'  # noqa: E731
lines = [f'# {P}: rate and distortion changes against mu = 0 (lambda {LAM}, S = {SMAP}; medians; bits and nMSE/lambda)', '',
         '| net kind | pairs at | mu | price | rate this | dist this | rate next | dist next | rate next at mu 0 | '
         'extra bits at matched distortion (pairs with both nMSE within 5%) | n |',
         '|' + '---|' * 11]
for key in sorted(rows, key=lambda k: (k[0] != 'relu', k[0], order.index(k[1]), k[2])):
    v = rows[key]
    g = lambda s: [x[s] for x in v]  # noqa: E731
    lines.append(f'| {key[0]} | {key[1]} | {key[2]} | {f(g("price"))} | {f(g("dR_this"))} | {f(g("dD_this"))} | '
                 f'{f(g("dR_next"))} | {f(g("dD_next"))} | {np.median(g("R0_next")):.2f} | '
                 f'{(f(mm) + f" ({len(mm)})") if (mm := [x for x in g("matched") if x is not None]) else "- (0)"} | {len(v)} |')
open(f'{W}/results/{P}_split.md', 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
