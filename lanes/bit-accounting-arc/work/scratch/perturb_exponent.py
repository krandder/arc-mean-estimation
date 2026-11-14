"""Diagnostic (not registered): how fast does the output error fall with the state error? For a state perturbation
delta = sigma * S^{1/2} xi (xi ~ N(0, I), S = Cov h_l: isotropic in whitened coordinates) at layer l, measure the output
nMSE D_out(sigma) = E|f(h + delta) - f(h)|^2 / tr Var a through the real net (float64), and its linearisation
D_lin(sigma) = E|J(h) delta|^2 / tr Var a (finite difference with a 1e-6 step). If D_out / D_lin < 1 and rises toward 1 as
sigma falls, the output error falls more slowly than the state error (local exponent alpha = dlog D_out / dlog sigma^2
< 1), and a code's bits per halving of the output RMS error exceed the number of directions it resolves.
usage: perturb_exponent.py <family> <seed> <layers comma> <out json>
"""
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gpu_src', 'lib'))
import vrlib as vr  # noqa: E402

fam, seed, layers, out = sys.argv[1], int(sys.argv[2]), [int(x) for x in sys.argv[3].split(',')], sys.argv[4]
Ws, act = vr.family_weights(fam, seed)
L = len(Ws)
n = Ws[0].shape[1]
P = 2048
rng = np.random.default_rng(12345 + seed)
x = rng.standard_normal((P, n))


def run(h, l0, l1=L):
    for k in range(l0, l1):
        h = h @ Ws[k].T
        if act == 'relu':
            h = np.maximum(h, 0.0)
    return h


res = dict(family=fam, seed=seed, P=P, layers={})
for l in layers:
    h = run(x, 0, l)
    a = run(h, l)
    V = a.var(0).sum()
    S = np.cov(h, rowvar=False)
    w, U = np.linalg.eigh(S)
    w = np.maximum(w, 0.0)
    S12 = (U * np.sqrt(w)) @ U.T
    xi = rng.standard_normal((P, n)) @ S12
    tau = 1e-6
    lin = (run(h + tau * xi, l) - a) / tau
    Dlin1 = (lin ** 2).sum(1).mean() / V          # D_lin at sigma = 1
    rows = []
    for s in np.logspace(-4, 0, 17):
        d = run(h + s * xi, l) - a
        Dout = (d ** 2).sum(1).mean() / V
        rows.append(dict(sigma=float(s), D_state=float(s * s * w.sum() / w.sum()), D_out=float(Dout),
                         D_lin=float(s * s * Dlin1), ratio=float(Dout / (s * s * Dlin1))))
    for r0, r1 in zip(rows, rows[1:]):
        r1['alpha'] = float(math.log(r1['D_out'] / r0['D_out']) / math.log((r1['sigma'] / r0['sigma']) ** 2))
    res['layers'][l] = rows
    print(fam, seed, 'l', l, ' '.join('%.0e:%.3g(%.2f,a=%.2f)' % (r['sigma'], r['D_out'], r['ratio'], r.get('alpha', float('nan')))
                                      for r in rows[::2]))
json.dump(res, open(out, 'w'), indent=1)
