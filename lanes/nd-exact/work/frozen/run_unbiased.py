"""Unbiased version (Amendment 1): the deterministic cube-sphere estimate D plus a sampled correction of the
within-cell residual, E[a] = D + E[f(x) - q(x)], q(x) = f(m_C) for x in open cell C (0 residual on certified cells).
The correction uses M inputs, plain MC or scrambled Sobol (inverse normal); f(x) = layers 1..32 then the certified
tail map J when the layer-32 state is in K (else the remaining layers). Cost = D's cost + M x (32 mv + inputs +
lookup + tail). Also reports Var(f - q) / Var(f), the share of the variance left within cells.
Usage: run_unbiased.py SEED LOG2_BUDGET_D LOG2M[,LOG2M...] R OUT.json
"""
import json
import math
import sys
import time

import numpy as np
from scipy.stats import norm, qmc

sys.path.insert(0, '/home/agent/workspaces/mats/work/nd-exact/frozen')
import cs2tree  # noqa: E402
import ndx  # noqa: E402

BASE = '/home/agent/workspaces/mats/work/nd-exact/'
PPF_MV = 8 * 96 / 128.0


def f_exact(est, X):
    """Full-net output: layers 1..c0 then J on K (exact there) or the remaining layers."""
    H = ndx.fwd(est.Ws, X, 0, est.c0)
    K = est.K
    out = np.zeros_like(H)
    g = H / np.maximum(np.abs(H[:, [K['i']]]), 1e-300)
    msk = np.ones(8, dtype=bool)
    msk[K['i']] = False
    inK = (K['s'] * H[:, K['i']] > 0) & np.all(g[:, msk] >= K['alpha'][msk], 1) & np.all(g[:, msk] <= K['beta'][msk], 1)
    out[inK] = H[inK] @ K['J'].T
    if (~inK).any():
        out[~inK] = ndx.fwd(est.Ws, H[~inK], est.c0, len(est.Ws))
    extra = float((~inK).sum()) * (len(est.Ws) - est.c0)
    return out, extra


def main():
    seed, lbD, R, outp = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[4]), sys.argv[5]
    lms = [int(v) for v in sys.argv[3].split(',')]
    Ws = ndx.make_weights(seed)
    tr = json.load(open(BASE + f'runs/truth_s{seed}.json'))
    mu, trV = np.array(tr['trunc_mean']), tr['trV']
    t0 = time.time()
    est = cs2tree.CS2(Ws, c0=32, Q=32, rule='surplus', floor=0.01)
    est.setup()
    while est.cost_mv() < 2.0 ** lbD and est.refine_one():
        pass
    D = est.estimate().copy()
    costD = est.cost_mv()
    out = dict(seed=seed, log2_budget_D=lbD, costD=costD, nmse_D=ndx.nmse(D, mu, trV), n_cells=est.n_cells,
               n_open=len(est.leafq), res={})
    rng = np.random.default_rng([4711, seed])
    for lm, kind in [(lm, k) for lm in lms for k in ('MC', 'RQMC')]:
        M = 1 << lm
        errs, ratios, costs = [], [], []
        for r in range(R):
            if kind == 'MC':
                X = rng.standard_normal((M, 8))
                in_mv = 1.0
            else:
                X = norm.ppf(np.clip(qmc.Sobol(d=8, scramble=True, seed=rng).random(M), 1e-300, 1 - 1e-16))
                in_mv = PPF_MV
            Qv, op, lf = cs2tree.lookup(est, X)
            F = np.zeros_like(X)
            extra = 0.0
            if op.any():
                F[op], extra = f_exact(est, X[op])
            res = F - Qv
            res[~op] = 0.0
            e = D + res.mean(0)
            errs.append(ndx.nmse(e, mu, trV))
            if kind == 'MC':
                Fall, _ = f_exact(est, X)
                ratios.append(float(res.var(0).sum() / Fall.var(0).sum()))
            costs.append(costD + M * (in_mv + 1.0) + op.sum() * est.c0 + extra + lf / 128.0 + M * 2.0)
        out['res'][f'{kind}_M{lm}'] = dict(nmse=float(np.mean(errs)), nmse_se=float(np.std(errs, ddof=1) / math.sqrt(R)),
                                cost_mv=float(np.mean(costs)), var_ratio=float(np.mean(ratios)) if ratios else None)
        print(seed, 'D 2^%d (nMSE %.2e, %d cells)' % (lbD, out['nmse_D'], est.n_cells), kind, 'M 2^%d' % lm,
              'nMSE %.3e cost %.3g mv' % (out['res'][f'{kind}_M{lm}']['nmse'], out['res'][f'{kind}_M{lm}']['cost_mv']),
              'Var(f-q)/Var(f) %s' % out['res'][f'{kind}_M{lm}']['var_ratio'], '(%.0fs)' % (time.time() - t0), flush=True)
    json.dump(out, open(outp, 'w'), indent=1)


if __name__ == '__main__':
    main()
