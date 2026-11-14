"""Amendment 2 scorer: gpt-6-astra's round-2 prediction for 512 x 64, tested on fresh nets 500-502 (no truths needed:
shares and gains come from rotation variances, V from the structure run's 2^12-sample estimate).
Writes results/score_a2.json and prints a markdown table."""
import json
import math
import os
import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
S = [500, 501, 502]
rows, have = [], []
sh = {}
for s in S:
    p = os.path.join(ROOT, 'runs', f'struct_n512_L64_s{s}.json')
    q = os.path.join(ROOT, 'runs', f'noise_n512_L64_s{s}.json')
    if not (os.path.exists(p) and os.path.exists(q)):
        continue
    r = json.load(open(p)); z = json.load(open(q))
    V, Vrb = r['V'], r['V_rb']; d = r['designs']
    rel = lambda k: d[k]['inv_gain_mc'] / (Vrb / V)
    sh[s] = dict(le2=1 - rel('simplex'), odd=r['V_odd'] / Vrb, g_simplex=1 / d['simplex']['inv_gain_mc'],
                 g_cross=1 / d['cross']['inv_gain_mc'], V=V, slope=z['gauss']['1e-05']['ns'][-1] / 1e-5)
    have.append(s)
k = len(have)
med = lambda key: float(np.median([sh[s][key] for s in have])) if have else float('nan')


def row(pid, text, val, ok):
    rows.append(dict(id=pid, prediction=text, measured=val,
                     result=('HOLDS' if ok else 'FAILS') if k == 3 else f'PARTIAL ({k} of 3 nets)'))


if have:
    row('PA5', '512 x 64: median degree <= 2 share in [0.45, 0.60]', round(med('le2'), 3), 0.45 <= med('le2') <= 0.60)
    row('PA6', '512 x 64: median odd share in [0.55, 0.59]', round(med('odd'), 3), 0.55 <= med('odd') <= 0.59)
    row('PA7', '512 x 64: median simplex gain in [1.8, 2.6] and cross-polytope gain in [2.0, 2.8]',
        (round(med('g_simplex'), 2), round(med('g_cross'), 2)),
        1.8 <= med('g_simplex') <= 2.6 and 2.0 <= med('g_cross') <= 2.8)
    nv = 512 / float(np.mean([sh[s]['V'] for s in have]))
    row('PA8', '512 x 64: n / (mean V over the nets) in [35, 45]', round(nv, 1), 35 <= nv <= 45)
    rows.append(dict(id='PA8-desc', prediction='median per-net output NS slope (descriptive)',
                     measured=round(med('slope'), 1), result='descriptive'))
json.dump(dict(per_net=sh, rows=rows), open(os.path.join(ROOT, 'results', 'score_a2.json'), 'w'), indent=1)
print('| id | prediction | measured | result |\n|---|---|---|---|')
for r_ in rows:
    print(f"| {r_['id']} | {r_['prediction']} | {r_['measured']} | {r_['result']} |")
