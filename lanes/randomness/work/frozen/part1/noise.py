"""Noise sensitivity and Gaussian surface area (GSA) of the gate partition and of the outputs, layer by layer, for one
net.

Two pair laws, each at correlation rho = 1 - delta:
- Gaussian (Ornstein-Uhlenbeck) pairs x, y = rho x + sqrt(1 - rho^2) z: per layer l, the expected number of gate flips
  F_l = E #{i : sign z_{l,i}(x) != sign z_{l,i}(y)}, the probability that the whole gate pattern of layers <= l
  changes, and the state's normalised decorrelation NS_l = E|h_l(x) - h_l(y)|^2 / (2 tr Var h_l). For a surface S with
  Gaussian surface area Gamma, P(x, y separated) = 2 sqrt(delta / pi) Gamma (1 + o(1)) as delta -> 0, so
  GSA_l(delta) = F_l / (2 sqrt(delta / pi)) estimates the summed GSA of the layer-l zero sets {z_{l,i} = 0}.
- Spherical pairs u, v with u . v = rho exactly: NS_sph = E|g(u) - g(v)|^2 / (2 tr Var g) of the output on the sphere.
  By Funk-Hecke, NS_sph(rho) = sum_{d>=1} E_d (1 - P_d(rho)) / sum_{d>=1} E_d exactly, with E_d the per-net harmonic
  energies (FORMAL T2), so the curve rho -> NS_sph gives exact linear functionals of the spectrum that designs probe.
Usage: noise.py seed n L [--P 4096] [--out PATH]
"""
import argparse
import json
import math
import os
import sys
import time
import numpy as np
import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))
import rnd  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('seed', type=int); ap.add_argument('n', type=int); ap.add_argument('L', type=int)
ap.add_argument('--P', type=int, default=4096)
ap.add_argument('--out', default=None)
a = ap.parse_args()
t0 = time.time()
n, L, P = a.n, a.L, a.P
net = rnd.Net(a.seed, n, L, dtype=torch.float64)
rng = np.random.default_rng([31337, a.seed, n, L])
deltas = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 3e-2, 0.1, 0.3, 1.0]
res = dict(seed=a.seed, n=n, L=L, P=P, deltas=deltas, gauss={}, sph={})


@torch.no_grad()
def run_pair(X, Y, chunk=2048):
    """Per-layer flips (sum), any-flip indicator up to l (sum), squared state differences (sum over pairs and units),
    and per-layer state sums / squared sums (for tr Var) over both members."""
    flips = np.zeros(L); anyf = np.zeros(L); d2 = np.zeros(L)
    s1 = np.zeros((L, n)); s2 = np.zeros(L); cnt = 0
    for i in range(0, X.shape[0], chunk):
        hx = torch.as_tensor(X[i:i + chunk]); hy = torch.as_tensor(Y[i:i + chunk])
        anyc = torch.zeros(hx.shape[0], dtype=torch.bool)
        for l in range(L):
            zx = hx @ net.Wt[l]; zy = hy @ net.Wt[l]
            fl = (zx > 0) != (zy > 0)
            flips[l] += float(fl.sum())
            anyc |= fl.any(dim=1)
            anyf[l] += float(anyc.sum())
            hx = torch.relu(zx); hy = torch.relu(zy)
            d2[l] += float(((hx - hy) ** 2).sum())
            s1[l] += (hx.sum(0) + hy.sum(0)).numpy()
            s2[l] += float((hx ** 2).sum() + (hy ** 2).sum())
        cnt += 2 * hx.shape[0]
    trvar = s2 / cnt - np.sum((s1 / cnt) ** 2, axis=1)
    return flips, anyf, d2, trvar


X = rng.standard_normal((P, n))
for dl in deltas:
    rho = 1.0 - dl
    Z = rng.standard_normal((P, n))
    Y = rho * X + math.sqrt(max(0.0, 1.0 - rho ** 2)) * Z
    flips, anyf, d2, trvar = run_pair(X, Y)
    F = flips / P
    res['gauss'][f'{dl:g}'] = dict(flips=F.tolist(), p_any=(anyf / P).tolist(),
                                   ns=(d2 / P / (2 * trvar)).tolist(),
                                   gsa=(F / (2 * math.sqrt(dl / math.pi))).tolist())
    print(f'[{time.time() - t0:6.1f}s] gauss delta={dl:g}: flips/layer l=1,{L // 2},{L}: {F[0]:.3g} {F[L // 2 - 1]:.3g} '
          f'{F[-1]:.3g}; p_any(L)={anyf[-1] / P:.3f}; NS_out={d2[-1] / P / (2 * trvar[-1]):.4g}; '
          f'GSA_1={F[0] / (2 * math.sqrt(dl / math.pi)):.4g} (n/sqrt(2pi)={n / math.sqrt(2 * math.pi):.4g})',
          flush=True)

# spherical pairs with exact inner product rho
U = rnd.to_sphere(rng.standard_normal((P, n)))
for dl in deltas:
    rho = 1.0 - dl
    Wv = rng.standard_normal((P, n))
    Wv -= np.sum(Wv * U, axis=1, keepdims=True) * U
    Wv = rnd.to_sphere(Wv)
    Vv = rho * U + math.sqrt(max(0.0, 1.0 - rho ** 2)) * Wv
    gu = net.outs(U); gv = net.outs(Vv)
    trv = float(np.sum(np.concatenate([gu, gv]).var(0)))
    ns = float(np.mean(np.sum((gu - gv) ** 2, axis=1)) / (2 * trv))
    res['sph'][f'{dl:g}'] = dict(rho=rho, ns_sph=ns, kernel=float(np.mean(np.sum(gu * gv, axis=1))))
    print(f'[{time.time() - t0:6.1f}s] sphere delta={dl:g}: NS_sph={ns:.4g}', flush=True)
res['seconds'] = time.time() - t0
out = a.out or os.path.join(os.path.dirname(__file__), '..', 'runs', f'noise_n{n}_L{L}_s{a.seed}.json')
with open(out, 'w') as fh:
    json.dump(res, fh)
print('done ->', out, flush=True)
