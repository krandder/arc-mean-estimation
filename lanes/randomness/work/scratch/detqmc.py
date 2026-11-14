"""Deterministic point sets (zero random bits) against the noiseless truth, for one net, as functions of N:
centred unscrambled Sobol (radius exact; and plain Gaussian), the same in the gate-aligned polar basis of W_1
(white-box, zero bits), Korobov rank-1 lattices (centred; baker-transformed), and the full k-wise independent
discretised-Gaussian designs over GF(q) (k = 2, 3, and 4 where affordable), plus the unrotated Kerdock design (n = 256).
Reports nMSE = |est - mu|^2 / V and nMSE x N (= 1 for plain MC in expectation), and log-log rate fits.
Usage: detqmc.py seed n L [--mmax 16] [--kmax 3] [--out PATH]
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
ap.add_argument('seed', type=int); ap.add_argument('n', type=int); ap.add_argument('L', type=int)
ap.add_argument('--mmax', type=int, default=16)
ap.add_argument('--kmax', type=int, default=3)
ap.add_argument('--kpoints_max', type=float, default=2.5e7)
ap.add_argument('--out', default=None)
a = ap.parse_args()
t0 = time.time()
n, L = a.n, a.L
net = rnd.Net(a.seed, n, L)
truth = rnd.load_truth(a.seed, n, L)
assert truth is not None, 'deterministic designs need a noiseless truth'
Qp = rnd.basis_polar(net.W64[0].numpy())
res = dict(seed=a.seed, n=n, L=L, truth_floor=truth['floor'], V=truth['V'], series={})


def rec(name, N, est):
    e = rnd.nmse(est, truth)
    res['series'].setdefault(name, []).append(dict(N=int(N), nmse=e, nmse_x_N=e * N))
    return e


def log(msg):
    print(f'[{time.time() - t0:7.1f}s] n={n} L={L} seed={a.seed} {msg}', flush=True)


for m in range(6, a.mmax + 1):
    N = 1 << m
    Pu = rnd.sobol_unit(m, n, scramble=False)
    Z = rnd.gauss_from_unit(Pu)
    e1 = rec('sobol_rb', N, rnd.rb_estimate(net, rnd.to_sphere(Z)))
    e2 = rec('sobol_plain', N, rnd.plain_estimate(net, Z))
    e3 = rec('sobol_rb_polar', N, rnd.rb_estimate(net, rnd.to_sphere(rnd.apply_basis(Z, Qp))))
    a_k, _ = rnd.korobov_a(N, n, cand=(256 if N <= 4096 else 48))
    Pl = rnd.lattice_unit(N, n, a=a_k)
    e4 = rec('lattice_rb', N, rnd.rb_estimate(net, rnd.to_sphere(rnd.gauss_from_unit(Pl))))
    Pb = rnd.lattice_unit(N, n, a=a_k, baker=True)
    e5 = rec('lattice_baker_rb', N, rnd.rb_estimate(net, rnd.to_sphere(rnd.gauss_from_unit(Pb))))
    log(f'N=2^{m}: nMSE x N sobol_rb {e1 * N:.3g} sobol_plain {e2 * N:.3g} sobol_rb_polar {e3 * N:.3g} '
        f'lattice_rb {e4 * N:.3g} lattice_baker_rb {e5 * N:.3g}')

# k-wise independent discretised Gaussians (full enumeration of GF(q)^k seeds), plain and radius-normalised
q = n + 1
while any(q % p == 0 for p in range(2, int(q ** 0.5) + 1)):
    q += 1
for k in range(2, a.kmax + 1):
    Ntot = q ** k
    if Ntot > a.kpoints_max:
        log(f'kwise k={k}: q^k = {Ntot:.3g} points > cap, skipped')
        continue
    grids = None
    s_plain = np.zeros(n); s_rb = np.zeros(n); cnt = 0; cnt_rb = 0
    # enumerate seeds in chunks: fix (a_1..a_{k-1}) blocks, vary a_0
    a0 = np.arange(q)
    blocks = np.stack(np.meshgrid(*[np.arange(q)] * (k - 1), indexing='ij'), -1).reshape(-1, k - 1)
    chunk_blocks = max(1, 16384 // q)
    for i in range(0, blocks.shape[0], chunk_blocks):
        B = blocks[i:i + chunk_blocks]
        seeds = np.concatenate([np.repeat(a0[None, :, None], B.shape[0], 0).reshape(-1, 1),
                                np.repeat(B, q, axis=0)], axis=1)
        X = rnd.kwise_gauss(k, n, q, seeds=seeds)
        s_plain += net.sum_out(X)
        nz = np.linalg.norm(X, axis=1) > 0                  # the all-zero point (one seed) has no direction
        s_rb += net.sum_out(rnd.to_sphere(X[nz]))
        cnt += X.shape[0]; cnt_rb += int(nz.sum())
    assert cnt == Ntot
    e6 = rec(f'kwise{k}_plain', Ntot, s_plain / Ntot)
    e7 = rec(f'kwise{k}_rb', Ntot, net.mn * s_rb / cnt_rb)
    log(f'kwise k={k} q={q} N={Ntot}: nMSE x N plain {e6 * Ntot:.3g} rb {e7 * Ntot:.3g}')

if n == 256:
    Kv = rnd.kerdock_bases(256).reshape(-1, 256)
    Kd = np.concatenate([Kv, -Kv])
    e8 = rec('kerdock_fixed_rb', Kd.shape[0], rnd.rb_estimate(net, Kd))
    e9 = rec('kerdock_polar_rb', Kd.shape[0], rnd.rb_estimate(net, rnd.apply_basis(Kd, Qp)))
    log(f'kerdock fixed: nMSE x N {e8 * Kd.shape[0]:.3g}; polar-aligned {e9 * Kd.shape[0]:.3g}')

# log-log slopes over N >= 2^8 (nMSE ~ N^-p)
for name, ser in res['series'].items():
    pts = [(s['N'], s['nmse']) for s in ser if s['N'] >= 256 and s['nmse'] > 3 * truth['floor']]
    if len(pts) >= 3:
        x = np.log([p[0] for p in pts]); y = np.log([p[1] for p in pts])
        res.setdefault('rate_p', {})[name] = float(-np.polyfit(x, y, 1)[0])
res['seconds'] = time.time() - t0
out = a.out or os.path.join(os.path.dirname(__file__), '..', 'runs', f'det_n{n}_L{L}_s{a.seed}.json')
with open(out, 'w') as fh:
    json.dump(res, fh, indent=1)
log(f'rates {res.get("rate_p")} -> {out}')
