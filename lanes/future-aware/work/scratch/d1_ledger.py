"""POST HOC (GPT-6 review rounds 1-2, finding 10): the D1 dedicated-cost window with the work C_ded leaves out.
C_ded (registered, hypothetical) = C(k2) + k + 1.5 k^4 / n^2 + 2n passes for the mean-field future at k = n/4. Left out:
(i) the separate K = 2 pilot that supplies the gate probabilities (+ C(k2));
(ii) the feature extraction at every hidden layer: the future directions are the top-k eigenvectors of the whitened
     relevance S^{1/2} R S^{1/2}. As implemented (lib/fa.py features + lib/fa_kprop.py whiten): two dense n x n
     eigensolves, the square root and three n x n products, ~26 n^3 flops per layer (an approximate count), i.e.
     ~13 n passes over L layers; an ASSUMED cheaper cost (the matrix-product arithmetic of Cholesky whitening plus a
     randomised range finder for the top k = n/4 with 10 oversampling columns): ~ n^3/3 + 12 n^2 (k + 10) flops per
     layer, ~2 n passes. This is assumed-cost arithmetic, not a specified feasible method: ARC's K = 3 states are
     indefinite (plain Cholesky fails at most layers; GPT-6 review round 3), orthogonalisation, the reduced eigensolve
     and feature normalisation are not itemised, and the accuracy of approximate directions is untested.
Gain = RQMC error at the cost / the method's error, median over nets (scorer's RQMC interpolation, slope -1 outside).
Side-effect free apart from writing results/d1_ledger.json."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score_helpers as S  # noqa: E402

out = {}
for n, L, seeds in S.CONF:
    k = n // 4
    feat_dense = 26.0 * n ** 3 * (L - 1) / (2.0 * n * n * L)
    feat_rand = (n ** 3 / 3.0 + 12.0 * n * n * (k + 10)) * (L - 1) / (2.0 * n * n * L)
    rows = {}
    for s in seeds:
        d = S.load('k3p', n, L, s)
        r = None if d is None else d['variants'].get(f'futmf2_{k}')
        if r is None or not np.isfinite(r['nmse']):
            continue
        cur = S.rqmc_curve(n, L, s)
        c0 = d['k2']['passes'] + k + 1.5 * k ** 4 / n ** 2 + 2.0 * n
        for name, C in (('C_ded', c0), ('+ K=2 pilot', c0 + d['k2']['passes']),
                        ('+ pilot + assumed ~2n-pass extraction', c0 + d['k2']['passes'] + feat_rand),
                        ('+ pilot + dense extraction (as implemented)', c0 + d['k2']['passes'] + feat_dense)):
            rows.setdefault(name, dict(C=[], G=[]))
            rows[name]['C'].append(C); rows[name]['G'].append(S.rqmc_err(cur, C)[0] / r['nmse'])
    out[n] = dict(feat_dense_passes=feat_dense, feat_rand_passes=feat_rand,
                  rows={k_: dict(C=S.med(v['C']), G=S.med(v['G']), G_range=[min(v['G']), max(v['G'])])
                        for k_, v in rows.items()})
json.dump(out, open(os.path.join(S.RES, 'd1_ledger.json'), 'w'), indent=1)
for n, v in out.items():
    print(f'n = {n}: feature extraction dense {v["feat_dense_passes"]:.0f} passes, randomised {v["feat_rand_passes"]:.0f}')
    for name, r in v['rows'].items():
        print(f'   {name:45s} C {r["C"]:.0f}  G {r["G"]:.2f} (nets {r["G_range"][0]:.2f}-{r["G_range"][1]:.2f})')
