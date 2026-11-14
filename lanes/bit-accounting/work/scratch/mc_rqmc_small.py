"""Part C reference: error of the output mean for plain MC and scrambled-Sobol RQMC on the small nets, against N.
Truth from 2^22 MC samples (its own error ~1/2^22 in nMSE units). Errors |est - E a|^2 / V averaged over R repetitions.
-> results/mc_rqmc_small.json"""
import json
import math
import os
import sys

import numpy as np
from scipy.stats import norm, qmc

sys.path.insert(0, '/home/agent/workspaces/mats/work/stationary/lib')
import st  # noqa: E402

CFG = [(16, 4), (32, 8), (16, 16), (32, 32)]
SEEDS = [5000, 5001, 5002]
NS = [2 ** k for k in range(4, 17, 2)]
R = 16
out = {}
for n, L in CFG:
    for s in SEEDS:
        WT = [np.ascontiguousarray(st.W_layer(s, n, k).T) for k in range(1, L + 1)]

        def F(X):
            h = X
            for W in WT:
                h = np.maximum(h @ W, 0.0)
            return h

        rng = np.random.default_rng(7 + s)
        tot, sq, cnt = 0.0, 0.0, 0
        for _ in range(64):
            A = F(rng.standard_normal((65536, n)))
            tot = tot + A.sum(0)
            sq = sq + (A * A).sum(0)
            cnt += A.shape[0]
        Ea = tot / cnt
        V = float((sq / cnt - Ea ** 2).sum())
        ent = dict(V=V, truth_err=1.0 / cnt, N=NS, mc=[], rqmc=[])
        for N in NS:
            e_mc, e_q = [], []
            for r in range(R):
                X = rng.standard_normal((N, n))
                e_mc.append(float(((F(X).mean(0) - Ea) ** 2).sum() / V))
                sob = qmc.Sobol(d=n, scramble=True, seed=int(rng.integers(1 << 31)))
                U = np.clip(sob.random(N), 1e-12, 1 - 1e-12)
                e_q.append(float(((F(norm.ppf(U)).mean(0) - Ea) ** 2).sum() / V))
            ent['mc'].append(float(np.mean(e_mc)))
            ent['rqmc'].append(float(np.mean(e_q)))
        ent['flops_per_sample'] = 2 * L * n * n
        out[f'n{n}_L{L}_s{s}'] = ent
        print(n, L, s, 'MC*N', [round(e * N, 2) for e, N in zip(ent['mc'], NS)], 'RQMC gain',
              [round(a / max(b, 1e-30), 1) for a, b in zip(ent['mc'], ent['rqmc'])], flush=True)
os.makedirs('results', exist_ok=True)
json.dump(out, open('results/mc_rqmc_small.json', 'w'))
