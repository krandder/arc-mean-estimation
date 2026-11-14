"""C7 table (Kelvin's single lambda-conditioned encoder against dedicated fixed-lambda models): for every dedicated model
(variants fixlam, fixlamlo: reference start; fixlamh1: look-ahead start), its held-out point (rate, nMSE) at its own
lambda, and the bits the variable-rate curves need for the same nMSE (reference start = base, mean of its restarts;
look-ahead start = h1), with the difference in percent and the registered C7 verdict (dedicated model better than the
variable-rate curve of the same start by more than max(restart spread, 3%, 0.5 bit) = fail).
usage: c7_table.py <runs base> <out md>
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import vrb  # noqa: E402

BASE, OUT = sys.argv[1], sys.argv[2]
runs, refs, idx = vrb.load(BASE)
START = {'fixlam': 'reference', 'fixlamlo': 'reference', 'fixlamh1': 'look-ahead'}


def f(x):
    return '-' if x is None else ('%.0f' % x if x >= 20 else '%.1f' % x)


L = ['| net | layer | class | dedicated start | t | dedicated bits | its nMSE | variable-rate bits, same start | '
     'variable-rate bits, other start | dedicated vs same start | C7 |', '|' + '---|' * 11]
for key in sorted(k for k in idx if k[4] in START):
    fam, seed, l, cls, var = key
    same = (vrb.base_runs(idx, fam, seed, l, cls) if START[var] == 'reference'
            else idx.get((fam, seed, l, cls, 'h1'), []))
    other = (idx.get((fam, seed, l, cls, 'h1'), []) if START[var] == 'reference'
             else vrb.base_runs(idx, fam, seed, l, cls))
    for r in sorted(idx[key], key=lambda r: r['fixed_t']):
        pt = min(r['pc'], key=lambda c: abs(c['t'] - r['fixed_t']))
        vs = [vrb.R_lin(b['pc'], pt['nmse']) for b in same]
        vs = [x for x in vs if x is not None]
        vo = [vrb.R_lin(b['pc'], pt['nmse']) for b in other]
        vo = [x for x in vo if x is not None]
        if vs:
            m = sum(vs) / len(vs)
            sp = max(vs) - min(vs)
            fail = pt['rate'] < min(vs) - max(sp, 0.03 * m, 0.5)
            d = f'{100 * (pt["rate"] - m) / m:+.0f}%'
            verdict = 'fail' if fail else 'pass'
        else:
            m, d, verdict = None, '-', 'variable-rate curve does not reach this nMSE'
        L.append(f'| {seed} | {l} | {cls} | {START[var]} | {r["fixed_t"]:.2f} | {f(pt["rate"])} | {pt["nmse"]:.4f} | '
                 f'{f(m)} | {f(min(vo)) if vo else "-"} | {d} | {verdict} |')
open(OUT, 'w').write('\n'.join(L) + '\n')
print('\n'.join(L))
