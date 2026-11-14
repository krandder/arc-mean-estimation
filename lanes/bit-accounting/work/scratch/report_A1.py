"""ARC 256 x 32 tables: linear codes (M1, all seeds), learned local codes (M2, where run), theory (RWF), and the
relevance lane's N(l, eps). -> results/A1_table.md"""
import json
import os

import numpy as np

SEEDS = [4000, 4001, 4002, 4003]
LAYERS = [0, 2, 4, 8, 16, 24, 31, 32]
REL = json.load(open('/home/agent/workspaces/mats/work/relevance/results/part1_scores.json'))


def lin(s, l, kind, e):
    p = f'runs/lin_arc_{s}.json'
    if not os.path.exists(p):
        return 'na'
    d = json.load(open(p))
    ent = d['layers'].get(str(l))
    if ent is None:
        return 'na'
    v = [ent[f'{b}_{kind}']['cross'][e][1] for b in ['as', 'lin'] if f'{b}_{kind}' in ent]
    v = [x for x in v if x is not None]
    return min(v) if v else None


def learned(s, l, kind, e):
    p = f'runs/A1_arc{s}_l{l}_{kind}.json'
    if not os.path.exists(p):
        return 'na'
    v = json.load(open(p))[f'b_{e}']
    return None if v[1] is None else v[1]


def th(s, l, e):
    p = f'results/theory_arc_{s}.json'
    if not os.path.exists(p):
        return 'na'
    d = json.load(open(p))
    if l == 32:
        return d['rwf_out'][e]
    return d['layers'][str(l)]['rwf_as'][e]


def relN(s, l, e):
    for c in REL['cells']:
        if c['mode'] == 'arc' and c['seed'] == s and c['l'] == l:
            return c[f'Nvec_{e}'][1]
    return 'na'


def fmt(vals):
    v = [x for x in vals if x != 'na']
    if not v:
        return '-'
    num = [x for x in v if x is not None]
    if not num:
        return '>256'
    srt = sorted([x if x is not None else float('inf') for x in v])
    k = len(srt)
    mid = srt[(k - 1) // 2: k // 2 + 1]
    s = '>256' if any(np.isinf(mid)) else f'{np.mean(mid):.0f}'
    if len(num) > 1:
        s += f' [{min(num):.0f}-{max(num):.0f}]'
    if len(num) < len(v):
        s += f' ({len(v) - len(num)} >256)'
    return s + (f' n={len(v)}' if len(v) < 4 else '')


lines = ['# ARC 256 x 32: bits per layer (median [min-max] over seeds 4000-4003; n = number of seeds if < 4)', '',
         'lin = linear transform code (best of active-subspace and degree-1 bases; analog channel C, Lloyd-Max FSQ b); '
         'learned = local L_2(512) code started at the linear code (train_bn2.py); RWF_as = reverse water-filling over '
         'the active-subspace spectrum (local high-resolution price; at "out" the output covariance); N = relevance '
         "lane's linear-feature count (upper value of its grid interval).", '']
for e in ['0.1', '0.01']:
    lines.append(f'## eps = {e}')
    lines.append('| layer | C lin | C learned | b lin (FSQ) | b learned (FSQ) | RWF_as / RWF_out | N(l, eps) |')
    lines.append('|---|---|---|---|---|---|---|')
    for l in LAYERS:
        row = [str(l) if l < 32 else 'out',
               fmt([lin(s, l, 'gauss', e) for s in SEEDS]), fmt([learned(s, l, 'gauss', e) for s in SEEDS]),
               fmt([lin(s, l, 'bin', e) for s in SEEDS]), fmt([learned(s, l, 'fsq', e) for s in SEEDS]),
               fmt([th(s, l, e) for s in SEEDS]),
               fmt([relN(s, l, e) for s in SEEDS]) if l in (0, 4, 8, 16, 24, 31) else '-']
        lines.append('| ' + ' | '.join(row) + ' |')
    lines.append('')
open('results/A1_table.md', 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
