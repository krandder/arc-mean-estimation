"""Exact one-step conditional moments of the two-replica chain at fixed (Q, delta, ell = 0), independent noise:
kappa_x = n Var(delta' | G) / delta^2 and the mean correction (E[delta'|G] - mf(delta)) n / delta, at delta = delta*(Q),
Q = 0.577 n. Also the per-layer variance of ell' (expected 4 delta/n + 2/(nQ))."""
import sys, json, math
sys.path.insert(0, '/home/agent/workspaces/mats/work/gram-chain/lib')
import numpy as np
import gc2

rng = np.random.default_rng(5)
out = {}
for n in (64, 256, 1024):
    Q = 0.5770780 * n
    for frac in (0.5, 1.0, 2.0):
        ds = float(gc2.mf_fixed_point(Q)[0]) * frac
        rho = 1 - ds
        G = np.array([[Q, Q * rho], [Q * rho, Q]])
        P = 400000 if n <= 256 else 100000
        acc_m, acc_v, acc_l = [], [], []
        for rep in range(4):
            Gp = gc2.step(np.repeat(G[None], P // 4, 0), n, rng)
            d = gc2.diffs(Gp, n, out_closed=False)
            acc_m.append(d['delta']); acc_l.append(d['ell'])
        dl = np.concatenate(acc_m); el = np.concatenate(acc_l)
        mf = (1 + Q * float(gc2.f_kernel(ds))) / (Q + 1)
        rec = dict(n=n, Q=Q, delta=ds, frac=frac, kappa_x=float(n * dl.var() / ds ** 2),
                   mean_corr_n_over_delta=float((dl.mean() - mf) * n / ds),
                   mean_corr_se=float(dl.std() / math.sqrt(dl.size) * n / ds),
                   var_ell_n_over_delta=float(el.var() * n / ds), pred_var_ell=float(4 + 2 / (Q * ds)))
        out['%d_%g' % (n, frac)] = rec
        print(rec, flush=True)
json.dump(out, open('/home/agent/workspaces/mats/work/gram-chain/results/onestep.json', 'w'), indent=1)
