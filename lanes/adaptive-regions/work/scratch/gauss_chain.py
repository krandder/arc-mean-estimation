"""Richer-state pattern chains (Kelvin via main, 3 Nov): per gate pattern s_l, keep a Gaussian (mass, mean, covariance
of h_l on {s_l = s}) or a K-component mixture; split it exactly-by-QMC through the next layer's gates (orthants of
z = W h), moment-match what lands in each next pattern, and merge down to K components per pattern.
MEASURED (exploratory); the orthant splits are scrambled-Sobol integrals of the closure Gaussian with 2^q points
(the closure, not the network, is integrated; accuracy checked by doubling q).
Layer 1 is exact up to QMC (x ~ N(0, I) exactly). K = 0 means no merging (components indexed by the whole pattern
path, i.e. one Gaussian per cell prefix).
Reported: N(0, I) output-mean nMSE vs an RQMC truth, state count (components summed over layers), vs MC / RQMC with
2^20 paths and the cell count.
Usage: gauss_chain.py SEED n [L=4] --Ks 1,2,4,8,0 --q 12
"""
import argparse, json, math, os, sys, time
import numpy as np
from scipy.stats import qmc
from scipy.special import ndtri
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import ar  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('seed', type=int); ap.add_argument('n', type=int); ap.add_argument('L', type=int, nargs='?', default=4)
ap.add_argument('--Ks', default='1,2,4,8,0')
ap.add_argument('--q', type=int, default=12)
ap.add_argument('--q1', type=int, default=20)
ap.add_argument('--log2truth', type=int, default=24)
ap.add_argument('--max_comp', type=int, default=200000)
ap.add_argument('--out', default=None)
args = ap.parse_args()
n, L, seed = args.n, args.L, args.seed
t0 = time.time()
W = [w.double().numpy() for w in ar.weights(seed, n, L)]


def fwd(X):
    h = X
    for l in range(L):
        h = np.maximum(h @ W[l].T, 0)
    return h


reps = []
for r_ in range(4):
    eng = qmc.Sobol(d=n, scramble=True, seed=seed * 1009 + 77 + r_); acc = np.zeros(n); NR = 1 << (args.log2truth - 2)
    for _ in range(max(1, NR >> 22)):
        acc += fwd(ndtri(np.clip(eng.random(min(NR, 1 << 22)), 1e-15, 1 - 1e-15))).sum(0)
    reps.append(acc / NR)
reps = np.array(reps); m0 = reps.mean(0)
Fv = fwd(np.random.RandomState(seed + 4242).standard_normal((1 << 20, n))); VF = float(Fv.var(0).sum())
truth_noise = float(reps.var(0, ddof=1).sum() / 4 / VF)
nm = lambda e: float(((e - m0) ** 2).sum() / VF)


def split(comps, l, rng):
    """comps: list of (mass, mean, cov, key) on h_l; returns dict next-pattern -> list of (mass, mean, cov, key)."""
    out = {}
    for (p, mu, S, key) in comps:
        ev, U = np.linalg.eigh(0.5 * (S + S.T)); R = U * np.sqrt(np.clip(ev, 0, None))
        shift = rng.random_sample(n)                                               # random shift of the QMC base
        Z = ndtri(np.clip((qmc_u + shift) % 1.0, 1e-15, 1 - 1e-15))
        h = mu + Z @ R.T
        z = h @ W[l + 1].T; g = z > 0; hn = z * g
        ids, inv, cnt = np.unique(np.packbits(g, axis=1), axis=0, return_inverse=True, return_counts=True)
        inv = inv.ravel(); M = len(h)
        for j in range(len(ids)):
            sel = inv == j; hs = hn[sel]; w = cnt[j] / M
            m_ = hs.mean(0); C = np.cov(hs.T, bias=True) if len(hs) > 1 else np.zeros((n, n))
            out.setdefault(ids[j].tobytes(), []).append((p * w, m_, np.atleast_2d(C), key + (ids[j].tobytes(),)))
    return out


def merge(lst, K):
    if K == 0 or len(lst) <= K:
        return lst
    lst = sorted(lst, key=lambda c: -c[0])
    keep, rest = lst[:K - 1], lst[K - 1:]
    P = sum(c[0] for c in rest); mu = sum(c[0] * c[1] for c in rest) / P
    S = sum(c[0] * (c[2] + np.outer(c[1] - mu, c[1] - mu)) for c in rest) / P
    return keep + [(P, mu, S, ('merged',))]


qmc_u = qmc.Sobol(d=n, scramble=False).random(1 << args.q)
res = dict(seed=seed, n=n, L=L, truth_noise=truth_noise, mc=2.0 ** -20, runs=[])
# layer 1 exact (QMC on x itself)
X1 = ndtri(np.clip(qmc.Sobol(d=n, scramble=True, seed=seed + 1).random(1 << args.q1), 1e-15, 1 - 1e-15))
z1 = X1 @ W[0].T; g1 = z1 > 0; h1 = z1 * g1
ids1, inv1, cnt1 = np.unique(np.packbits(g1, axis=1), axis=0, return_inverse=True, return_counts=True); inv1 = inv1.ravel()
layer1 = []
for j in range(len(ids1)):
    hs = h1[inv1 == j]
    layer1.append((cnt1[j] / len(h1), hs.mean(0), np.cov(hs.T, bias=True) if len(hs) > 1 else np.zeros((n, n)), (ids1[j].tobytes(),)))
for K in [int(k) for k in args.Ks.split(',')]:
    t1 = time.time(); rng = np.random.RandomState(seed + 17)
    comps = [c for c in layer1]; states = len(comps); ok = True
    for l in range(L - 1):
        nxt = split(comps, l, rng)
        comps = []
        for t, lst in nxt.items():
            comps += merge(lst, K)
        states += len(comps)
        if len(comps) > args.max_comp:
            ok = False; break
    if not ok:
        res['runs'].append(dict(K=K, states=states, err=None, note='too many components')); continue
    est = sum(c[0] * c[1] for c in comps)
    r = dict(K=K, states=states, final_components=len(comps), err=nm(est), secs=time.time() - t1)
    res['runs'].append(r)
    print(f"K={K if K else 'inf'}: states {states}, err {r['err']:.2e} ({r['secs']:.0f}s)", flush=True)
rq = []
for r_ in range(4):
    eng = qmc.Sobol(d=n, scramble=True, seed=seed * 31 + r_)
    rq.append(nm(fwd(ndtri(np.clip(eng.random(1 << 20), 1e-15, 1 - 1e-15))).mean(0)))
res['rqmc'] = float(np.mean(rq))
print(f'MC(2^20) {res["mc"]:.1e}, RQMC(2^20) {res["rqmc"]:.1e}, truth noise {truth_noise:.1e}', flush=True)
out = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs', f'gauss_chain_n{n}_L{L}_s{seed}_q{args.q}.json')
json.dump(res, open(out, 'w'), default=float)
