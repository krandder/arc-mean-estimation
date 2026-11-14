"""Registered head-to-head at ARC's budget (256 x 32; N = 2^16 points ~ 6.5e4 passes), one net: structured samplers
with decreasing randomness, all radius exact unless stated, errors against the noiseless truth.
  rqmc_std      scrambled Sobol (LMS + digital shift) in the standard (black-box) frame          R replicates
  rqmc_polar    the same in the polar frame of W_1 (white-box gate alignment)                    R replicates
  kerdock       antipodal 5-design (129 MUBs + antipodes, 66,048 points), one Haar rotation      R replicates
  mc_pairwise   pairwise-independent MC: X_i = Phi^-1((U + i V) mod 1), U, V uniform (2 n b bits) R replicates
  det_std       centred unscrambled Sobol, standard frame (zero random bits)                     1
  det_polar     centred unscrambled Sobol, polar frame (zero random bits, white-box)              1
Per method: mean nMSE over replicates (vs truth), replicate variance x N / V, and the gain over plain MC (1/N).
Usage: combo.py seed [--R 16] [--m 16] [--out PATH]
"""
import argparse
import json
import math
import os
import sys
import time
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))
import rnd  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('seed', type=int)
ap.add_argument('--n', type=int, default=256); ap.add_argument('--L', type=int, default=32)
ap.add_argument('--R', type=int, default=16); ap.add_argument('--m', type=int, default=16)
ap.add_argument('--out', default=None)
a = ap.parse_args()
t0 = time.time()
n, L = a.n, a.L
net = rnd.Net(a.seed, n, L)
truth = rnd.load_truth(a.seed, n, L)
assert truth is not None
V = truth['V']
N = 1 << a.m
Qp = rnd.basis_polar(net.W64[0].numpy())
rng = np.random.default_rng([4711, a.seed, n, L])
res = dict(seed=a.seed, n=n, L=L, N=N, R=a.R, V=V, truth_floor=truth['floor'], methods={})


def log(msg):
    print(f'[{time.time() - t0:7.1f}s] seed={a.seed} {msg}', flush=True)


def summarize(name, ests, npts, bits):
    ests = np.atleast_2d(np.array(ests))
    errs = np.sum((ests - truth['mean']) ** 2, axis=1) / V
    out = dict(points=int(npts), reps=int(ests.shape[0]), random_bits=bits, nmse_mean=float(errs.mean()),
               nmse_reps=errs.tolist(), gain_mc=float(1.0 / (errs.mean() * npts)))
    if ests.shape[0] > 1:
        var = float(np.sum(ests.var(0, ddof=1)))
        out['rep_var_x_N_over_V'] = var * npts / V
    res['methods'][name] = out
    log(f'{name}: points={npts} nMSE={errs.mean():.3e} gain_mc={out["gain_mc"]:.3f} '
        f'repvar*N/V={out.get("rep_var_x_N_over_V", float("nan")):.3f}')


b = 32                                   # bits per coordinate assumed in the random-bit accounting
for frame, Q in (('std', None), ('polar', Qp)):
    ests = []
    for r in range(a.R):
        Pu = rnd.sobol_unit(a.m, n, scramble=True, seed=90_000 * a.seed + 1000 + r + (0 if Q is None else 500))
        Z = rnd.gauss_from_unit(Pu)
        U = rnd.to_sphere(Z if Q is None else rnd.apply_basis(Z, Q))
        ests.append(rnd.rb_estimate(net, U))
    summarize(f'rqmc_{frame}', ests, N, n * b * (b - 1) // 2 + n * b)
Kv = rnd.kerdock_bases(256).reshape(-1, 256)
Kd = np.concatenate([Kv, -Kv])
ests = []
for r in range(a.R):
    ests.append(rnd.rb_estimate(net, rnd.rotate(Kd, rnd.haar(n, rng))))
summarize('kerdock', ests, Kd.shape[0], n * (n - 1) // 2 * b)
ests = []
for r in range(a.R):
    U0 = rng.random(n); V0 = rng.random(n)
    i = np.arange(1, N + 1)[:, None]
    P = (U0[None, :] + i * V0[None, :]) % 1.0
    Z = rnd.gauss_from_unit(np.clip(P, 1e-15, 1 - 1e-15))
    ests.append(rnd.rb_estimate(net, rnd.to_sphere(Z)))
summarize('mc_pairwise', ests, N, 2 * n * b)
Pu = rnd.sobol_unit(a.m, n, scramble=False)
Z = rnd.gauss_from_unit(Pu)
summarize('det_std', [rnd.rb_estimate(net, rnd.to_sphere(Z))], N, 0)
summarize('det_polar', [rnd.rb_estimate(net, rnd.to_sphere(rnd.apply_basis(Z, Qp)))], N, 0)
res['seconds'] = time.time() - t0
out = a.out or os.path.join(os.path.dirname(__file__), '..', 'runs', f'combo_n{n}_L{L}_s{a.seed}.json')
with open(out, 'w') as fh:
    json.dump(res, fh, indent=1)
log(f'done -> {out}')
