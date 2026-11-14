"""How fast does the deterministic cube-sphere code converge on ONE ReLU layer, by width (exact truth available)?

E[relu(W x)]_j = |w_j| / sqrt(2 pi), x ~ N(0, I_n), W iid N(0, 2/n) (nd.make_weights family). nMSE normalised by
tr Var(relu(W x)) = sum_j |w_j|^2 (1/2 - 1/(2 pi)). The code is lib/cs2.py with c0 = L = 1 (adaptive, surplus rule with a mass floor (Amendment 1), exact
on certified cells). Compared with MC (nMSE = 1/N) and RQMC (scrambled Sobol) at equal cost in mv.
Usage: depth1_rate.py OUT.json
"""
import json
import math
import sys
import time

import numpy as np
from scipy.stats import norm, qmc

sys.path.insert(0, '/home/agent/workspaces/mats/work/nd-exact/lib')
import cs2  # noqa: E402
import ndx  # noqa: E402


def main():
    outp = sys.argv[1]
    res = []
    for n in (2, 3, 4, 6, 8):
        for seed in (103, 111):
            W = ndx.make_weights(seed, n=n, L=1)
            exact = np.linalg.norm(W[0], axis=1) / math.sqrt(2 * math.pi)
            trV = float((np.linalg.norm(W[0], axis=1) ** 2).sum() * (0.5 - 1 / (2 * math.pi)))
            est = cs2.CS2(W, c0=1, Q=32, rule='surplus_m', floor=0.01, mfloor=0.01, face_floor=True)
            est.setup()
            t0 = time.time()
            pts = []
            nxt = 4
            while True:
                if est.n_cells >= 2 ** nxt:
                    pts.append(dict(cells=est.n_cells, cost_mv=est.cost_mv(),
                                    nmse=ndx.nmse(est.estimate(), exact, trV), P_cert=est.P_cert))
                    nxt += 1
                    if nxt > 17 or time.time() - t0 > 600:
                        break
                if not est.refine_one():
                    pts.append(dict(cells=est.n_cells, cost_mv=est.cost_mv(),
                                    nmse=ndx.nmse(est.estimate(), exact, trV), P_cert=est.P_cert, exhausted=True))
                    break
            # RQMC on the same layer at a few point counts (cost 1 mv + n inverse normals per point)
            rq = []
            rng = np.random.default_rng([77, n, seed])
            for m in (2 ** k for k in range(4, 18, 2)):
                e = []
                for r in range(16):
                    X = norm.ppf(np.clip(qmc.Sobol(d=n, scramble=True, seed=rng).random(m), 1e-300, 1 - 1e-16))
                    e.append(ndx.nmse(np.maximum(X @ W[0].T, 0).mean(0), exact, trV))
                rq.append(dict(points=m, cost_mv=m * (1 + n * 96 / 128.0), nmse=float(np.mean(e))))
            res.append(dict(n=n, seed=seed, cs=pts, rqmc=rq))
            last = pts[-1]
            print('n %d seed %d: CS cells %d cost %.3g mv nMSE %.2e certified %.3f | RQMC 2^16 pts nMSE %.2e' % (
                n, seed, last['cells'], last['cost_mv'], last['nmse'], last['P_cert'], rq[-1]['nmse']), flush=True)
            json.dump(res, open(outp, 'w'), indent=1)


if __name__ == '__main__':
    main()
