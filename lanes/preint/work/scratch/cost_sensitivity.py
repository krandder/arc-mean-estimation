"""Post hoc (review findings 5 and round-2 item 4): sensitivity of the registered PI comparisons to the cost ledger.
The registered nominal ledger charges, per final vertex, two Student-t cdfs and one power. lib/line.py evaluates four
cdfs and two powers per finite piece and does not charge ray arithmetic or the crossing sort; PI_as's pilot SVD is
charged 4 d P^2 (P = 64), which overstates a thin SVD when P > d (4 P d^2 would do).
  A: + (2 cdf + 1 power + 20 sort/ray FLOPs) per final vertex per line (cdf = 200 FLOPs)
  B: as A with the cdf priced at 400 FLOPs (four cdfs at 400 instead of two at 200)
  C: as A, and PI_as's SVD charged 4 P d^2 instead of 4 d P^2 (lowers PI_as's fixed cost on the small nets)
MLMC's uncharged draws are not adjusted here. Comparators as registered: RQMCRB for small nets (P4), RQMCJ for
8 x 256 (P5a), RQMC for the ladder and 256 x 32 (P3a). Split run files are merged per net (scratch/score.load).
Writes results/cost_sensitivity.json and prints per-family ranges and the overall maxima."""
import copy
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from score import alpha, interp, load  # noqa: E402

ROOT = os.path.join(HERE, '..')
F_CDF, F_POW = 200, 16


def adjust(rows, n, L, scen, method):
    pf = 2.0 * n * n * L
    out = copy.deepcopy(rows)
    cdf = 2 * F_CDF if scen == 'B' else F_CDF
    for r in out:
        v = r.get('vertices_mean', 0.0)
        extra = r['N'] * v * (4 * cdf - 2 * F_CDF + F_POW + 20) / pf
        if scen == 'C' and method.startswith('PI_as') or scen == 'C' and method.startswith('PIJ_as'):
            d, P = n, 64
            extra -= max(0.0, 4.0 * d * P * P - 4.0 * P * d * d) / pf
        r['cost'] = r['cost'] + extra
    return out


def min_ratio(pi_rows, ref_rows):
    vals = []
    for c in ref_rows:
        v = interp(pi_rows, c['cost'])
        if np.isfinite(v):
            vals.append(v / c['nmse_rep'])
    return min(vals) if vals else float('nan')


def main():
    res = []
    for pattern, ref in (('s1_small_*.json', 'RQMCRB'), ('s2_nd_*.json', 'RQMCJ'), ('s3_arc_*.json', 'RQMC')):
        for key, d in sorted(load(pattern).items()):
            n, L = d['n'], d['L']
            M = d['methods']
            if ref not in M:
                continue
            for m in [k for k in M if k.startswith('PI')]:
                base = M[m]
                if not base or 'vertices_mean' not in base[-1]:
                    continue
                rec = dict(net=list(key), method=m, ref=ref, alpha=alpha(base)[0], min_ratio=min_ratio(base, M[ref]))
                for sc in ('A', 'B', 'C'):
                    adj = adjust(base, n, L, sc, m)
                    rec['cost_factor_' + sc] = adj[-1]['cost'] / base[-1]['cost']
                    rec['alpha_' + sc] = alpha(adj)[0]
                    rec['min_ratio_' + sc] = min_ratio(adj, M[ref])
                res.append(rec)
    json.dump(res, open(os.path.join(ROOT, 'results', 'cost_sensitivity.json'), 'w'), indent=1)
    fam = {}
    for r in res:
        k = '%s %dx%d' % (r['net'][0], r['net'][1], r['net'][2])
        fam.setdefault(k, []).append(r)
    for k, v in sorted(fam.items()):
        print('%-14s cost x%.3f-%.3f (A) x%.3f-%.3f (B) x%.3f-%.3f (C) | alpha shift A %+.3f..%+.3f B %+.3f..%+.3f C %+.3f..%+.3f | min ratio change A %.2f..%.2f' % (
            k, min(x['cost_factor_A'] for x in v), max(x['cost_factor_A'] for x in v),
            min(x['cost_factor_B'] for x in v), max(x['cost_factor_B'] for x in v),
            min(x['cost_factor_C'] for x in v), max(x['cost_factor_C'] for x in v),
            min(x['alpha_A'] - x['alpha'] for x in v), max(x['alpha_A'] - x['alpha'] for x in v),
            min(x['alpha_B'] - x['alpha'] for x in v), max(x['alpha_B'] - x['alpha'] for x in v),
            min(x['alpha_C'] - x['alpha'] for x in v), max(x['alpha_C'] - x['alpha'] for x in v),
            min(x['min_ratio_A'] / x['min_ratio'] for x in v), max(x['min_ratio_A'] / x['min_ratio'] for x in v)))
    ok = [r for r in res if np.isfinite(r['alpha_A'])]
    print('records %d; max |alpha shift| A %.3f B %.3f C %.3f; PI still worse than its comparator at every common cost '
          'in scenario A on %d of %d records' % (
              len(res), max(abs(r['alpha_A'] - r['alpha']) for r in ok), max(abs(r['alpha_B'] - r['alpha']) for r in ok),
              max(abs(r['alpha_C'] - r['alpha']) for r in ok), sum(1 for r in res if r['min_ratio_A'] > 1), len(res)))


if __name__ == '__main__':
    main()
