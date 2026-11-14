"""Small nets: best code found per (net, layer, class), channel bits C(eps) and sign/FSQ bits b(eps), median [range]
over seeds 5000-5002. Local best = min(learned local, linear transform code); unrestricted = learned unres (upper bound
on the output's count, training-limited) and the output-space best = min(learned output code, linear output code).
-> results/S1_best.md"""
import json
import math
import os

import numpy as np

RATES = [1, 2, 3, 4, 6, 8, 12, 16, 24, 32]
EVAL = [5000, 5001, 5002]


def crossing(rates, y, eps):
    y = np.minimum.accumulate(np.asarray(y, float))
    for i in range(len(rates)):
        if y[i] <= eps:
            if i == 0:
                return float(rates[0])
            y0, y1 = math.log(max(y[i - 1], 1e-30)), math.log(max(y[i], 1e-30))
            f = (y0 - math.log(eps)) / (y0 - y1) if y0 != y1 else 1.0
            return float(rates[i - 1] + f * (rates[i] - rates[i - 1]))
    return None


def learned(n, L, s, l, cls, kind, e):
    p = f'runs/S_curves/S_n{n}_L{L}_s{s}_l{l}_{cls}.json'
    if not os.path.exists(p):
        return 'na'
    return crossing(RATES, json.load(open(p))['curves'][kind]['nmse'], e)


def lin(n, L, s, l, kind, e):
    p = f'runs/lin_small{n}x{L}_{s}.json'
    if not os.path.exists(p):
        return 'na'
    ent = json.load(open(p))['layers'].get(str(l))
    if ent is None:
        return 'na'
    v = [ent[f'{b}_{kind}']['cross'][str(e)][1] for b in ['as', 'lin'] if f'{b}_{kind}' in ent]
    v = [x for x in v if x is not None]
    return min(v) if v else None


def best(*vals):
    v = [x for x in vals if x != 'na']
    if not v:
        return 'na'
    num = [x for x in v if x is not None]
    return min(num) if num else None


def fmt(vals):
    v = [x for x in vals if x != 'na']
    if not v:
        return '-'
    srt = sorted([x if x is not None else float('inf') for x in v])
    k = len(srt)
    mid = srt[(k - 1) // 2: k // 2 + 1]
    s = '>32' if any(np.isinf(mid)) else f'{np.mean(mid):.1f}'
    num = [x for x in v if x is not None]
    if len(num) > 1:
        s += f' [{min(num):.1f}-{max(num):.1f}]'
    if len(num) < len(v):
        s += f' ({len(v) - len(num)} >32)'
    return s


lines = ['# Small nets: bits per layer, best code found (median [range] over seeds 5000-5002; ">32" not reached)', '',
         'C = channel capacity bits; b = binary bits (learned: sign bits; linear: Lloyd-Max FSQ bits). local = one ReLU '
         'layer of width n (best of the learned code and the linear transform code, which the class contains); unres = '
         'learned encoder that also sees the exact output (1500 steps; an upper bound on the output-space count, see '
         'the 3000-step check); out = output space (best of learned and linear).', '']
for n, L in [(16, 4), (32, 8), (16, 16), (32, 32)]:
    grid = sorted(set([0, L // 4, L // 2, (3 * L) // 4, L - 1]))
    lines.append(f'## {n} x {L}')
    lines.append('| layer | C(0.1) local | C(0.1) unres | C(0.01) local | C(0.01) unres | b(0.1) local | b(0.1) unres | C(0.001) local |')
    lines.append('|---|---|---|---|---|---|---|---|')
    for l in grid + [L]:
        if l < L:
            row = [str(l)]
            for e in [0.1, 0.01]:
                row.append(fmt([best(learned(n, L, s, l, 'local', 'gauss', e), lin(n, L, s, l, 'gauss', e)) for s in EVAL]))
                row.append(fmt([learned(n, L, s, l, 'unres', 'gauss', e) for s in EVAL]))
            row.append(fmt([best(learned(n, L, s, l, 'local', 'bin', 0.1), lin(n, L, s, l, 'bin', 0.1)) for s in EVAL]))
            row.append(fmt([learned(n, L, s, l, 'unres', 'bin', 0.1) for s in EVAL]))
            row.append(fmt([best(learned(n, L, s, l, 'local', 'gauss', 0.001), lin(n, L, s, l, 'gauss', 0.001)) for s in EVAL]))
        else:
            row = ['out', fmt([best(learned(n, L, s, L, 'unres', 'gauss', 0.1), lin(n, L, s, L, 'gauss', 0.1)) for s in EVAL]),
                   '', fmt([best(learned(n, L, s, L, 'unres', 'gauss', 0.01), lin(n, L, s, L, 'gauss', 0.01)) for s in EVAL]),
                   '', fmt([best(learned(n, L, s, L, 'unres', 'bin', 0.1), lin(n, L, s, L, 'bin', 0.1)) for s in EVAL]), '',
                   fmt([best(learned(n, L, s, L, 'unres', 'gauss', 0.001), lin(n, L, s, L, 'gauss', 0.001)) for s in EVAL])]
        lines.append('| ' + ' | '.join(row) + ' |')
    lines.append('')
open('results/S1_best.md', 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
