"""Bounds on the output's own rate for the small nets (Kelvin's item 4): Gaussian upper bound R_G(eps V; Cov a) and a
Shannon-type lower bound from the top-k principal projections: any code with E|a - a_hat|^2 <= D codes the projection
u_k = Q_k^T (a - m) with E|u_k - u_k_hat|^2 <= D, so R_a(D) >= R_{u_k}(D) >= h(u_k) - (k/2) log2(2 pi e D / k) (Shannon
lower bound), with h(u_k) estimated by the Kozachenko-Leonenko k-NN estimator (k = 1, 2, 3 projections). The best of
k = 1, 2, 3 is reported (an estimate: the entropy estimator has its own error). -> results/bounds_small.json"""
import json
import math
import os
import sys

import numpy as np
from scipy.spatial import cKDTree
from scipy.special import digamma, gammaln

sys.path.insert(0, '/home/agent/workspaces/mats/work/stationary/lib')
import st  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import rwf  # noqa: E402


def kl_entropy_bits(X, k=3):
    """Kozachenko-Leonenko differential entropy estimate (bits) of rows of X (N, d)."""
    N, d = X.shape
    tree = cKDTree(X)
    r, _ = tree.query(X, k=k + 1)
    eps = np.maximum(r[:, -1], 1e-300)
    log_vd = (d / 2) * math.log(math.pi) - gammaln(d / 2 + 1)
    h_nats = digamma(N) - digamma(k) + log_vd + d * np.mean(np.log(eps))
    return h_nats / math.log(2)


out = {}
for n, L in [(16, 4), (32, 8), (16, 16), (32, 32)]:
    for s in [5000, 5001, 5002]:
        rng = np.random.default_rng(99 + s)
        WT = [np.ascontiguousarray(st.W_layer(s, n, k).T) for k in range(1, L + 1)]
        h = rng.standard_normal((65536, n))
        for W in WT:
            h = np.maximum(h @ W, 0.0)
        A = h
        V = float(A.var(0).sum())
        ev, Q = np.linalg.eigh(np.cov(A, rowvar=False))
        ev, Q = ev[::-1], Q[:, ::-1]
        U = (A - A.mean(0)) @ Q
        ent = dict(V=V, rwf={}, slb={})
        for e in [0.1, 0.01, 0.001]:
            ent['rwf'][str(e)] = rwf.rwf_rate(ev, e * V)
            best = 0.0
            for k in (1, 2, 3):
                hk = kl_entropy_bits(U[:, :k] + 1e-9 * rng.standard_normal((U.shape[0], k)))
                lb = hk - (k / 2) * math.log2(2 * math.pi * math.e * e * V / k)
                best = max(best, lb)
            ent['slb'][str(e)] = best
        out[f'n{n}_L{L}_s{s}'] = ent
        print(n, L, s, 'RWF', {k: round(v, 2) for k, v in ent['rwf'].items()}, 'SLB', {k: round(v, 2) for k, v in ent['slb'].items()},
              flush=True)
json.dump(out, open('results/bounds_small.json', 'w'))
