"""S7 tables: bits used for nMSE eps when the encoder chooses (lambda sweep), per arm, layer and class; checks.
-> results/S7_table.md, results/S7_summary.json"""
import glob
import json
import math
import os

import numpy as np

EVAL = [5000, 5001, 5002]
ARMS = ['gfix', 'bern', 'ent', 'vib']


def rate_at(rates, nmse, eps):
    """Smallest rate on the lower envelope of the (rate, nMSE) sweep reaching eps (log-linear between neighbours)."""
    pts = sorted(zip(rates, nmse))
    env = []
    best = float('inf')
    for r, e in pts:
        if e < best:
            env.append((r, e))
            best = e
    for i, (r, e) in enumerate(env):
        if e <= eps:
            if i == 0:
                return r
            r0, e0 = env[i - 1]
            f = (math.log(e0) - math.log(eps)) / (math.log(e0) - math.log(max(e, 1e-30)))
            return r0 + f * (r - r0)
    return None


def load(p):
    return json.load(open(p)) if os.path.exists(p) else None


def med(v):
    v = [x for x in v if x != 'na']
    if not v:
        return '-'
    srt = sorted([x if x is not None else float('inf') for x in v])
    k = len(srt)
    mid = srt[(k - 1) // 2: k // 2 + 1]
    s = 'unreached' if any(np.isinf(mid)) else f'{np.mean(mid):.1f}'
    num = [x for x in v if x is not None]
    if len(num) > 1:
        s += f' [{min(num):.1f}-{max(num):.1f}]'
    return s


lines = ['# S7: bits the encoder chooses to use (lambda sweep), median [range] over seeds', '',
         'gfix (primary) = fixed unit Gaussian noise, encoder-chosen scale, rate = information estimate with a learned '
         'prior; bern = Bernoulli bits, rate = sum_j I(h; b_j); ent = uniform noise, rounding, entropy-coded rate; vib = '
         'encoder-chosen variance, N(0, I) prior KL. R(eps) = bits per sample at which the sweep reaches nMSE eps.', '']
summary = {}
for n, L in [(16, 4), (32, 8), (16, 16), (32, 32)]:
    grid = sorted(set([0, L // 4, L // 2, (3 * L) // 4, L - 1]))
    files = [p for p in glob.glob(f'runs/S_ent/E_n{n}_L{L}_s*_l*_*.json')]
    if not files:
        continue
    lines.append(f'## {n} x {L}')
    lines.append('| layer | class | ' + ' | '.join(f'{a} R(0.1)' for a in ARMS) + ' | gfix R(0.01) | gfix refit/trained | bern bits at p~0.5 (largest lambda) |')
    lines.append('|---|---|' + '---|' * (len(ARMS) + 3))
    for l in grid + [L]:
        for cls in (['local', 'unres'] if l < L else ['unres']):
            rs = [load(f'runs/S_ent/E_n{n}_L{L}_s{s}_l{l}_{cls}.json') for s in EVAL]
            rs = [r for r in rs if r is not None]
            if not rs:
                continue
            row = [str(l) if l < L else 'out', cls]
            for a in ARMS:
                row.append(med([rate_at(r['curves'][a]['rate'], r['curves'][a]['nmse'], 0.1) if a in r['curves'] else 'na' for r in rs]))
            row.append(med([rate_at(r['curves']['gfix']['rate'], r['curves']['gfix']['nmse'], 0.01) for r in rs if 'gfix' in r['curves']]))
            ratio = [np.mean([rf / max(rt, 1e-9) for rf, rt in zip(r['curves']['gfix']['rate_refit'], r['curves']['gfix']['rate']) if rt > 0.5])
                     for r in rs if 'gfix' in r['curves'] and 'rate_refit' in r['curves']['gfix']]
            row.append(f'{np.median(ratio):.3f}' if ratio else '-')
            half = [np.mean([h > 0.5 for h in r['curves']['bern']['bits_half'][0]]) for r in rs if 'bern' in r['curves']]
            row.append(f'{np.median(half):.2f}' if half else '-')
            lines.append('| ' + ' | '.join(row) + ' |')
            summary[f'{n}x{L}_l{l}_{cls}'] = {a: [rate_at(r['curves'][a]['rate'], r['curves'][a]['nmse'], 0.1) for r in rs if a in r['curves']] for a in ARMS}
    lines.append('')
os.makedirs('results', exist_ok=True)
open('results/S7_table.md', 'w').write('\n'.join(lines) + '\n')
json.dump(summary, open('results/S7_summary.json', 'w'))
print('\n'.join(lines))
