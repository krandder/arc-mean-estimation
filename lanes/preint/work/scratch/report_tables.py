"""Markdown tables for preint.md sections 4.1-4.3 from runs/s1_*, s2_*, s3_* and results/posthoc_matched.json.
Writes results/tables.md."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
from score import load, alpha, interp, common_ratio  # noqa: E402

sys.path.insert(0, os.path.join(ROOT, 'frozen'))
import line as LN  # noqa: E402


def f(x, p=2):
    return ('%.' + str(p) + 'f') % x if x is not None and np.isfinite(x) else '-'


def matched(rows_pi, rows_ref):
    """v2 (after co-prover round 2): intersection of N ranges (PI's upper two thirds); slopes per N on the same N
    values; equivalent points per line r^{1/alpha_ref} with r the variance ratio at matched N."""
    lo = rows_pi[len(rows_pi) // 3]['N']
    bp = {r['N']: r['nmse_rep'] for r in rows_pi}
    br = {r['N']: r['nmse_rep'] for r in rows_ref}
    Ns = sorted(N for N in bp if N in br and N >= lo)
    if len(Ns) < 3:
        return float('nan'), float('nan'), float('nan'), (Ns[0] if Ns else 0), (Ns[-1] if Ns else 0)
    X = np.log(Ns)
    spi = -np.polyfit(X, np.log([bp[N] for N in Ns]), 1)[0]
    sref = -np.polyfit(X, np.log([br[N] for N in Ns]), 1)[0]
    r = np.array([br[N] / bp[N] for N in Ns])
    eq = float(np.median(r ** (1.0 / sref))) if sref > 0 else float('nan')
    return spi, sref, eq, Ns[0], Ns[-1]


def at_cost(rows, c):
    return interp(rows, c) if rows else float('nan')


def main():
    out = []
    s1 = load('s1_small_*.json')
    out.append('### 4.1 Small nets (exponent = top-60% fit of log nMSE on log cost; 16 replicates)\n')
    out.append('| net (n x L, seed) | RQMC | RQMCRB | PI_as | PI_rand | constructive upper-bound exponents RB / PI (another algorithm) [A] | PI_as / RQMCRB at equal cost (largest common budget) | matched N: slope per N, PI_as vs RQMCRB | equivalent points per line (matched N) | passes per line |')
    out.append('|' + '---|' * 10)
    for k, d in sorted(s1.items()):
        M = d['methods']
        n = k[1]
        ratios = common_ratio(M['PI_as'], M['RQMCRB'])
        spi, sref, worth, lo, hi = matched(M['PI_as'], M['RQMCRB'])
        out.append('| %dx%d s%d | %s | %s | %s | %s | %s / %s | %s | %s vs %s (N %d-%d) | %s | %.0f |' % (
            n, k[2], k[3], f(alpha(M['RQMC'])[0]), f(alpha(M['RQMCRB'])[0]), f(alpha(M['PI_as'])[0]),
            f(alpha(M['PI_rand'])[0]), f(1 + 3.0 / (n - 1)), f(1 + 5.0 / (n - 2)),
            f(ratios[-1], 1) if ratios else '-', f(spi), f(sref), lo, hi, f(worth, 1),
            M['PI_as'][-1]['cost'] / M['PI_as'][-1]['N']))
    s2 = load('s2_nd_*.json')
    out.append('\n### 4.2 Narrow-deep 8 x 256 (8 replicates; nMSE at 2^13 passes interpolated)\n')
    out.append('| net | RQMC | RQMCRB | RQMCJ | PIJ_as | PIJ_rand | MLMC_32 | nMSE at 8192 passes: RQMCJ / PIJ best / MLMC | min PIJ / RQMCJ at equal cost | matched N slope PIJ_as vs RQMCJ | equivalent points per line (matched N) | passes per PIJ line |')
    out.append('|' + '---|' * 12)
    for k, d in sorted(s2.items()):
        M = d['methods']
        c0 = 8192.0
        best = min(at_cost(M.get('PIJ_as'), c0), at_cost(M.get('PIJ_rand'), c0))
        ratios = []
        for c in M['RQMCJ']:
            vals = [interp(M[m], c['cost']) for m in ('PIJ_as', 'PIJ_rand')]
            vals = [v for v in vals if np.isfinite(v)]
            if vals:
                ratios.append(min(vals) / c['nmse_rep'])
        spi, sref, worth, lo, hi = matched(M['PIJ_as'], M['RQMCJ'])
        out.append('| %d | %s | %s | %s | %s | %s | %s | %.1e / %.1e / %.1e | %s | %s vs %s | %s | %.0f |' % (
            k[3], f(alpha(M['RQMC'])[0]), f(alpha(M['RQMCRB'])[0]), f(alpha(M['RQMCJ'])[0]),
            f(alpha(M['PIJ_as'])[0]), f(alpha(M['PIJ_rand'])[0]),
            f(alpha(M['MLMC_32'])[0]) if 'MLMC_32' in M else '-',
            at_cost(M['RQMCJ'], c0), best, at_cost(M.get('MLMC_32'), c0) if 'MLMC_32' in M else float('nan'),
            f(min(ratios), 1) if ratios else '-', f(spi), f(sref), f(worth, 1),
            M['PIJ_as'][-1]['cost'] / M['PIJ_as'][-1]['N']))
    s3 = load('s3_arc_*.json')
    out.append('\n### 4.3 Ladder at L = n/8 and ARC 256 x 32 (8 replicates)\n')
    out.append('| net | RQMC | RQMCRB | PI_as_w | PI_rand_w | MLMC | N x nMSE of RQMC at its last 3 budgets | min PI / RQMC at equal cost | matched N slope PI_as_w vs RQMCRB | equivalent points per line (matched N) | passes per line (as / rand) | window vertices / law | line variance ratio rand / as |')
    out.append('|' + '---|' * 13)
    for k, d in sorted(s3.items(), key=lambda kv: (kv[0][1], kv[0][3])):
        M = d['methods']
        n, L = k[1], k[2]
        mm = [m for m in M if m.startswith('MLMC')]
        mrows = [r for r in M[mm[0]] if r['p'] >= 8] if mm else None     # registered MLMC budgets 2^8..2^14
        ratios = []
        for c in M['RQMC']:
            vals = [interp(M[m], c['cost']) for m in ('PI_as_w', 'PI_rand_w') if m in M]
            vals = [v for v in vals if np.isfinite(v)]
            if vals:
                ratios.append(min(vals) / c['nmse_rep'])
        pmj = [r for r in json.load(open(os.path.join(ROOT, 'results', 'posthoc_matched.json')))
               if r['file'] == 's3_arc_n%d_L%d_s%d.json' % (n, L, k[3]) and r['method'] == 'PI_as_w']
        if pmj:
            spi, sref, worth = pmj[0]['slope_pi'], pmj[0]['slope_ref'], pmj[0]['equiv_points_per_line_median']
        elif 'PI_as_w' in M and 'RQMCRB' in M:
            spi, sref, worth, lo, hi = matched(M['PI_as_w'], M['RQMCRB'])
        else:
            spi = sref = worth = float('nan')
        wt = LN.Weight('student', n - 1)
        pred = 3 + n * L * 2 * math.atan(wt.window(1e-8)) / math.pi
        vr_r = M['PI_rand_w'][-1]['line_var_ratio'] if 'PI_rand_w' in M else float('nan')
        vr_a = M['PI_as_w'][-1]['line_var_ratio'] if 'PI_as_w' in M else float('nan')
        vert = M['PI_rand_w'][-1]['vertices_mean'] / pred if 'PI_rand_w' in M else float('nan')
        cpl = '%.0f / %.0f' % (M['PI_as_w'][-1]['cost'] / M['PI_as_w'][-1]['N'] if 'PI_as_w' in M else float('nan'),
                               M['PI_rand_w'][-1]['cost'] / M['PI_rand_w'][-1]['N'] if 'PI_rand_w' in M else float('nan'))
        out.append('| %dx%d s%d | %s | %s | %s | %s | %s | %s | %s | %s vs %s | %s | %s | %s | %s / %s |' % (
            n, L, k[3], f(alpha(M['RQMC'])[0]), f(alpha(M['RQMCRB'])[0]) if 'RQMCRB' in M else '-',
            f(alpha(M['PI_as_w'])[0]) if 'PI_as_w' in M else '-',
            f(alpha(M['PI_rand_w'])[0]) if 'PI_rand_w' in M else '-',
            f(alpha(mrows)[0]) if mm else '-',
            ', '.join('%.2f' % (r['N'] * r['nmse_rep']) for r in M['RQMC'][-3:]),
            f(min(ratios), 0) if ratios else '-', f(spi), f(sref), f(worth, 1), cpl, f(vert), f(vr_r), f(vr_a)))
    open(os.path.join(ROOT, 'results', 'tables.md'), 'w').write('\n'.join(out) + '\n')
    print('\n'.join(out))


if __name__ == '__main__':
    main()
