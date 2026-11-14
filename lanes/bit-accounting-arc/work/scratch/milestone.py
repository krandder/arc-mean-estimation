"""Compact view of one net's cells (A4 conventions): R(eps) per restart and variant, the analytic references, the
Gaussian bound, refit ratios and decoder diagnostics. usage: milestone.py <runs base> <family> <seed> <layers csv>"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import vra  # noqa: E402
import vrb  # noqa: E402

BASE, FAM, SEED = sys.argv[1], sys.argv[2], int(sys.argv[3])
LAYERS = [int(x) for x in sys.argv[4].split(',')]
EPS = [0.3, 0.1, 0.03, 0.01, 0.003, 0.001]
runs, refs, idx = vrb.load(BASE)


def f(v):
    return '   -  ' if v is None else ('%6.0f' % v if v >= 20 else '%6.2f' % v)


print('eps:', EPS)
out = vrb.base_runs(idx, FAM, SEED, vrb.LOUT[FAM], 'out', restarts=(0, 1, 2))
if out:
    print(f'{"Gaussian bound":30s}' + ' '.join(f(vra.gauss_bound(out[0]['out_evals'], out[0]['V'], e)) for e in EPS))
for l in LAYERS:
    for (fa, s, ll, c, v), rs in sorted(idx.items()):
        if fa != FAM or s != SEED or ll != l:
            continue
        for d in sorted(rs, key=lambda d: (str(d['restart']), str(d['fixed_t']))):
            Rs = [vrb.R_lin(d['pc'], e) for e in EPS]
            ratios = [min(x for x in (cc.get('rate_refit_tri'), cc.get('rate_refit_fact'), cc.get('rate_refit_gauss'))
                          if x is not None) / cc['rate'] for cc in d['curve']
                      if cc['rate'] > 5 and any(cc.get(k) is not None for k in ('rate_refit_tri', 'rate_refit_fact'))]
            tag = f"l{l} {c} {v} " + (f"r{d['restart']}" if d['restart'] is not None else f"t{d['fixed_t']}")
            print(f'{tag:30s}' + ' '.join(f(r) for r in Rs) + f"   refit/trained min {min(ratios):.3f}" if ratios else
                  f'{tag:30s}' + ' '.join(f(r) for r in Rs))
    rf = refs.get((FAM, SEED, l))
    if rf:
        for kind in ('gram', 'mean', 'gauss'):
            print(f'{"l%d ref %s" % (l, kind):30s}' + ' '.join(f(vrb.R_lin(rf['refs'][kind]['curve'], e)) for e in EPS))
