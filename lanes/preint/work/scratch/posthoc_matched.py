"""Post hoc (not registered), v2 after co-prover round 2: compare PI and point rules at matched N (lines vs points).
For each net and PI variant, over the INTERSECTION of the two curves' N ranges (PI's upper two thirds):
  slope of log nMSE on log N for PI and for the point rule (both on the same N values),
  variance ratio r(N) = nMSE_point(N) / nMSE_PI(N) at matched N (median), and the equivalent number of points per line
  r^{1/alpha} (alpha = the point rule's per-N slope there; r alone is a variance ratio, not a point count),
  and the cost per line in passes.
Usage: posthoc_matched.py PATTERN [PATTERN ...]; writes results/posthoc_matched.json"""
import glob
import json
import os
import sys

import numpy as np


def slope_se(X, Y):
    A = np.vstack([X, np.ones_like(X)]).T
    coef, _, _, _ = np.linalg.lstsq(A, Y, rcond=None)
    if X.size <= 2:
        return -coef[0], float('nan')
    resid = Y - A @ coef
    s2 = (resid ** 2).sum() / (X.size - 2)
    return -coef[0], float(np.sqrt(s2 / ((X - X.mean()) ** 2).sum()))


def merged(files):
    """Merge per-net files (scored s3 parts, s201_b) and, for 256 x 32, the post-hoc small-N point runs
    (runs/posthoc_smallN_*), which replace the reference rows at N <= 64 (16 replicates)."""
    nets = {}
    for f in files:
        d = json.load(open(f))
        key = (d['family'], d['n'], d['L'], d['seed'])
        if key in nets:
            nets[key]['methods'].update(d['methods'])
        else:
            nets[key] = d
            nets[key]['file'] = os.path.basename(f)
    for key, d in nets.items():
        if key[1] == 256:
            sp = os.path.join('runs', 'posthoc_smallN_n256_L32_s%d.json' % key[3])
            if os.path.exists(sp):
                small = json.load(open(sp))['methods']
                for m, rows in small.items():
                    big = [r for r in d['methods'].get(m, []) if r['N'] > 64]
                    d['methods'][m] = rows + big
    return nets


def main():
    files = []
    for p in sys.argv[1:]:
        files += sorted(glob.glob(p))
    out = []
    for key, d in sorted(merged(files).items()):
        f = d['file']
        M = d['methods']
        for pm in [m for m in M if m.startswith('PI')]:
            rows = M[pm]
            if len(rows) < 4:
                continue
            ref = 'RQMCJ' if pm.startswith('PIJ') else ('RQMCRB' if 'RQMCRB' in M else 'RQMC')
            if ref not in M:
                continue
            lo_pi = rows[len(rows) // 3]['N']
            byN_ref = {r['N']: r['nmse_rep'] for r in M[ref]}
            byN_pi = {r['N']: r['nmse_rep'] for r in rows}
            Ns = sorted(N for N in byN_pi if N in byN_ref and N >= lo_pi)
            if len(Ns) < 3:
                continue
            X = np.log(Ns)
            s_pi, se_pi = slope_se(X, np.log([byN_pi[N] for N in Ns]))
            s_ref, se_ref = slope_se(X, np.log([byN_ref[N] for N in Ns]))
            r = np.array([byN_ref[N] / byN_pi[N] for N in Ns])
            eq = r ** (1.0 / s_ref) if s_ref > 0 else r * np.nan
            cpl = rows[-1]['cost'] / rows[-1]['N']
            rec = dict(file=f.split('/')[-1], method=pm, ref=ref, Nlo=int(Ns[0]), Nhi=int(Ns[-1]), slope_pi=float(s_pi),
                       slope_ref=float(s_ref), slope_pi_se=se_pi, slope_ref_se=se_ref, npts=len(Ns),
                       var_ratio_median=float(np.median(r)),
                       equiv_points_per_line_median=float(np.median(eq)), cost_per_line_passes=float(cpl))
            out.append(rec)
            print('%-30s %-10s vs %-6s N %5d-%5d  slope/N PI %.2f ref %.2f | variance ratio %.2f, equivalent points %.2f | %.0f passes/line' % (
                rec['file'], pm, ref, Ns[0], Ns[-1], s_pi, s_ref, rec['var_ratio_median'],
                rec['equiv_points_per_line_median'], cpl))
    json.dump(out, open('results/posthoc_matched.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
