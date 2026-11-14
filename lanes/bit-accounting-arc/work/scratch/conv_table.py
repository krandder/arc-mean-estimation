"""Convergence table for the report (C3 and the added checks A9/A11): for every cell with certificate variants, the bits
needed at each accuracy by the base (mean of restarts 0-1, or restart 0 where only it ran), restart 2, 2x steps, 2x
depth, 4x steps, depth 6 with 4x steps, and the look-ahead start; plus each variant's change relative to the base.
usage: conv_table.py <runs base> <out md>
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import vrb  # noqa: E402

BASE, OUT = sys.argv[1], sys.argv[2]
runs, refs, idx = vrb.load(BASE)
EPS = [0.1, 0.03, 0.01, 0.003, 0.001]
VARS = [('r2', 'restart 2'), ('steps2', '2x steps'), ('cap2', '2x depth'), ('steps4', '4x steps'),
        ('cap2steps2', 'depth 6 + 2x steps'), ('cap2steps4', 'depth 6 + 4x steps'), ('cap2steps8', 'depth 6 + 8x steps'),
        ('h1', 'look-ahead start'), ('h1s2', 'look-ahead, 2x steps'), ('h1s4', 'look-ahead, 4x steps'),
        ('h1s8', 'look-ahead, 8x steps'), ('h1c2', 'look-ahead, depth 6'), ('h1c2s2', 'look-ahead, depth 6 + 2x steps')]


def f(x):
    if x is None:
        return '-'
    if not math.isfinite(x):
        return 'unreached'
    return '%.0f' % x if x >= 20 else '%.1f' % x


L = ['| net | layer | class | run | ' + ' | '.join(f'nMSE {e}' for e in EPS) + ' |', '|' + '---|' * (4 + len(EPS))]
cells = sorted({(k[0], k[1], k[2], k[3]) for k in idx if k[4] in ('steps2', 'cap2', 'steps4', 'cap2steps4', 'cap2steps8',
                                                                   'h1s8')})
for fam, seed, l, cls in cells:
    base = vrb.base_runs(idx, fam, seed, l, cls)
    r2 = [r for r in idx.get((fam, seed, l, cls, 'base'), []) if r.get('restart') == 2]
    if base:
        rows = [('base (restarts %s)' % ','.join(str(r['restart']) for r in base), base)]
    else:   # base pending: compare with restart 2
        rows, base = [('base (restart 2; restarts 0-1 pending)', r2)], r2
    for v, name in VARS:
        if v == 'r2' and base is r2:
            continue
        rs = r2 if v == 'r2' else idx.get((fam, seed, l, cls, v), [])
        if rs:
            rows.append((name, rs))
    bvals = {e: (vrb.cellR(base, e) or {}).get('mean') for e in EPS}
    for name, rs in rows:
        vals = []
        for e in EPS:
            c = vrb.cellR(rs, e)
            x = c['mean'] if c else None
            s = f(x)
            b = bvals[e]
            if name.startswith('base') or x is None or b is None or not math.isfinite(x) or not math.isfinite(b):
                vals.append(s)
            else:
                vals.append(f'{s} ({100 * (x - b) / b:+.0f}%)')
        L.append(f'| {seed} | {l} | {cls} | {name} | ' + ' | '.join(vals) + ' |')
open(OUT, 'w').write('\n'.join(L) + '\n')
print('\n'.join(L))

# A13: the optimiser's reach (10x encoder learning rate), relative to the same start at the default rate
L2 = ['', '| net | layer | start | run | ' + ' | '.join(f'nMSE {e}' for e in EPS) + ' |', '|' + '---|' * (4 + len(EPS))]
for key in sorted(k for k in idx if k[4] in ('h1lr', 'reflr')):
    fam, seed, l, cls, v = key
    ref_rs = idx.get((fam, seed, l, cls, 'h1'), []) if v == 'h1lr' else vrb.base_runs(idx, fam, seed, l, cls)
    start = 'look-ahead' if v == 'h1lr' else 'reference'
    for name, rs in (('lr 3e-5 (default)', ref_rs), ('lr 3e-4 (10x)', idx[key])):
        vals = []
        for e in EPS:
            c = vrb.cellR(rs, e)
            x = c['mean'] if c else None
            b = (vrb.cellR(ref_rs, e) or {}).get('mean')
            s = f(x)
            if name.startswith('lr 3e-4') and x is not None and b is not None and math.isfinite(x) and math.isfinite(b):
                s += f' ({100 * (x - b) / b:+.0f}%)'
            vals.append(s)
        L2.append(f'| {seed} | {l} | {start} | {name} | ' + ' | '.join(vals) + ' |')
open(OUT, 'a').write('\n'.join(L2) + '\n')
print('\n'.join(L2))
