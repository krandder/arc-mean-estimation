"""Fixed-sample LP (no column generation) vs N, for the finite-support check. MEASURED (exploratory).
Same nets as cg.py (n=4, net0, L=1,2,4,8), d=4 and 6, N = 2^12 .. 2^16 Gaussian-mixture points."""
import json, math, numpy as np
from cg import Herm, build, unit
from mm import make_net, net_f, sample_points
n = 4
Xtest = np.random.default_rng(99).standard_normal((1 << 16, n))
nets = {L: make_net(n, L, 0, Xtest) for L in (1, 2, 4, 8)}
G = np.random.default_rng(777).standard_normal((1 << 20, n))
sds = {L: float(net_f(G, Ws, a, L).std()) for L, (Ws, a, _) in nets.items()}
Xall = sample_points(n, 1 << 16, seed=123)
for d in (4, 6):
    herm = Herm(n, d)
    for N in (1 << 12, 1 << 13, 1 << 14, 1 << 15, 1 << 16):
        X = Xall[:N]; A = herm.matrix(X)
        h = build(A, np.zeros(N))
        for L, (Ws, a, _) in nets.items():
            f = net_f(X, Ws, a, L); v = {}
            for s in (1, -1):
                h.changeColsCost(N, np.arange(N, dtype=np.int32), -s * f)
                h.run(); v[s] = -s * h.getObjectiveValue() if h.modelStatusToString(h.getModelStatus()) == "Optimal" else float("nan")
            rec = {"n": n, "d": d, "N": N, "L": L, "gap_sd": (v[1] - v[-1]) / sds[L]}
            print(json.dumps(rec), flush=True)
