"""Gamma_d/sd for single last-layer ReLU units of random He-ReLU nets, vs width n, depth L, order d.
MEASURED.  Gamma_d is the PROVEN upper bound (see oned_bound.py docstring) on the layer-wise
order-d ambiguity of E relu(t) for that unit; it depends only on the law of t under P0."""
import json, math, sys, numpy as np
from gamma1d import gamma_d
out = sys.argv[1]
N = 20000
ds = [2, 3, 4, 6, 8, 12]
for n in [8, 16, 32, 64, 128, 256]:
    X = np.random.default_rng([7, n]).standard_normal((N, n))
    w = np.full(N, 1 / N)
    for L in [1, 2, 4, 8, 16, 32]:
        for k in range(3):
            rng = np.random.default_rng([n, L, k, 12345])
            h = X
            for l in range(L - 1):
                h = np.maximum(h @ (rng.standard_normal((n, n)) * math.sqrt(2 / n)).T, 0)
            z = h @ (rng.standard_normal((n, n)) * math.sqrt(2 / n)).T
            units = [i for i in range(n) if np.std(np.maximum(z[:, i], 0)) > 1e-12][:6]
            for i in units:
                t = z[:, i]
                m, s = t.mean(), t.std()
                y = (t - m) / s
                rec = dict(n=n, L=L, net=k, unit=i, kurt=float(np.mean(y ** 4)), p_zero=float(np.mean(np.abs(t) < 1e-12)),
                           p_pos=float(np.mean(t > 1e-12)), p_neg=float(np.mean(t < -1e-12)), g={})
                for d in ds:
                    g, sdr = gamma_d(t, w, d)
                    rec["g"][d] = None if g is None else g / sdr
                with open(out, "a") as fo:
                    fo.write(json.dumps(rec) + "\n")
            print(n, L, k, flush=True)
