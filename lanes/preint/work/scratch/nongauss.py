"""Non-Gaussianity of the random-net prior at finite L/n (FORMAL F9; descriptive, post hoc).
For K random nets of the ARC family (fresh seeds 10000 + i) and two fixed random unit inputs x1, x2 (shared by all
nets), per net: f(x1), f(x2), the pre-activations z_L(x1), the norm |h_L(x1)|, and E_x f from 2^10 radius-exact RQMC
points (scrambled Sobol) with the per-net angular variance V(net) = tr Var_x f(xhat) from the same points.
Pooled over units and nets, excess kurtosis of:
  (a) unit outputs f_j(x1) (rectified);  (b) pre-activations z_j(x1);  (c) f_j(x1) - f_j(x2);
  (d) the one-point error f_j(x1) - (E f)_j;  (e) Var over nets of log |h_L(x1)|^2 (Hanin-Nica scale: ~5 L / n);
  (f) the one-point error divided by the net's own RMS, sqrt(V(net) / n). Descriptive only: this normalisation does
      NOT reduce a pure Gaussian scale mixture to zero excess kurtosis (it leaves sign(Z), excess kurtosis -2; co-prover
      round 2). log |h_L|^2 is clipped at 1e-300 for nets with a dead output.
Usage: nongauss.py N L K OUT.json"""
import json
import math
import os
import sys

import numpy as np
from scipy.special import ndtri
from scipy.stats import qmc

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import est as E  # noqa: E402
import line as LN  # noqa: E402
import nets  # noqa: E402


def exkurt(v):
    v = np.asarray(v, dtype=float).ravel()
    v = v - v.mean()
    s2 = (v ** 2).mean()
    return float((v ** 4).mean() / s2 ** 2 - 3.0) if s2 > 0 else float('nan')


def main():
    n, L, K, outp = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    rng0 = np.random.default_rng([31415, n, L])
    x = rng0.standard_normal((2, n))
    x /= np.linalg.norm(x, axis=1, keepdims=True)
    F1, F2, Z1, LN2, ERR, ERRN = [], [], [], [], [], []
    cm = LN.chi_mean(n)
    for i in range(K):
        Ws = nets.arc_weights(10000 + i, n, L)
        h = x.copy()
        for W in Ws[:-1]:
            h = np.maximum(h @ W.T, 0.0)
        z = h @ Ws[-1].T
        f = np.maximum(z, 0.0)
        eng = qmc.Sobol(d=n, scramble=True, seed=np.random.default_rng([2718, i]))
        U = ndtri(np.clip(eng.random_base2(10), 1e-300, 1 - 1e-16))
        U /= np.linalg.norm(U, axis=1, keepdims=True)
        G = E.forward(Ws, U)
        mean_ang = G.mean(0)                       # E_xhat f(xhat) (estimate)
        V = float(G.var(0).sum())                  # tr Var_xhat f(xhat)
        F1.append(f[0]); F2.append(f[1]); Z1.append(z[0])
        LN2.append(math.log(max((f[0] ** 2).sum(), 1e-300)))
        e = f[0] - mean_ang
        ERR.append(e)
        ERRN.append(e / math.sqrt(max(V / n, 1e-300)))
    F1, F2, Z1, ERR, ERRN = map(np.array, (F1, F2, Z1, ERR, ERRN))
    res = dict(n=n, L=L, K=K,
               exkurt_unit_output=exkurt(F1), exkurt_preact=exkurt(Z1), exkurt_angular_diff=exkurt(F1 - F2),
               exkurt_one_point_error=exkurt(ERR), exkurt_one_point_error_scaled=exkurt(ERRN),
               var_log_norm2=float(np.var(LN2)), hanin_nica_5L_over_n=5.0 * L / n,
               frac_zero_units=float((F1 == 0).mean()))
    json.dump(res, open(outp, 'w'), indent=1)
    print(json.dumps(res), flush=True)


if __name__ == '__main__':
    main()
