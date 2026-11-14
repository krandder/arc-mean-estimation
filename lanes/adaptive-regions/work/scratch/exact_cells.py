"""Exact-cell estimator for small nets ("understand every region", exact form), MEASURED (exploratory).

f(x) = h_L is linear on each joint gate-pattern cone C_P = {x : sign pattern P}: f = A_P x there, so
E f = sum_P A_P E[x 1_{C_P}], and for a polyhedral cone C = {x : g_j . x >= 0} (divergence theorem, PROVEN; the facet
formula of FORMAL.md E1 [A]):  E[x 1_C] = (2 pi)^{-1/2} sum_j (g_j / |g_j|) P_{n-1}(F_j),
with P_{n-1}(F_j) the Gaussian measure of the facet cone inside g_j^perp. At n = 4 a facet is a 3-D polyhedral cone and
its Gaussian measure is its solid angle / (4 pi) (spherical polygon area, exact). Patterns are the ones seen among the
advice paths (training samples); held-out coverage of those patterns is reported, so unseen cells are visible.
Cost: arithmetic only, no network passes. Compared against MC / RQMC with the same number of advice paths.
Usage: exact_cells.py SEED [n=4] [L=4] [--log2train 20] [--log2truth 26]
"""
import argparse, json, math, os, sys, time
import numpy as np
import torch
from scipy.stats import qmc
from scipy.special import ndtri
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import ar  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('seed', type=int); ap.add_argument('n', type=int, nargs='?', default=4); ap.add_argument('L', type=int, nargs='?', default=4)
ap.add_argument('--log2train', type=int, default=20)
ap.add_argument('--log2truth', type=int, default=26)
ap.add_argument('--selftest', action='store_true')
ap.add_argument('--out', default=None)
args = ap.parse_args()
n, L, seed = args.n, args.L, args.seed
assert n == 4, 'facet measure implemented for n = 4 (3-D facet cones)'
TOL = 1e-12


def solid_angle_cone3(H):
    """Gaussian measure of {y in R^3 : H y >= 0} (rows of H = constraint normals) = solid angle / (4 pi)."""
    H = H[np.linalg.norm(H, axis=1) > 1e-12]
    if len(H) == 0:
        return 1.0
    Hn = H / np.linalg.norm(H, axis=1, keepdims=True)
    # dedupe identical normals
    keep = []
    for i, h in enumerate(Hn):
        if all(np.abs(h - Hn[j]).max() > 1e-10 for j in keep):
            keep.append(i)
    Hn = Hn[keep]
    if any(np.abs(Hn[i] + Hn[j]).max() < 1e-10 for i in range(len(Hn)) for j in range(i)):
        return 0.0                                                       # y.h >= 0 and y.h <= 0: measure zero
    m = len(Hn)
    if m == 1:
        return 0.5
    # candidate extreme rays: intersections of constraint planes
    verts = []
    for a in range(m):
        for b in range(a + 1, m):
            v = np.cross(Hn[a], Hn[b]); nv = np.linalg.norm(v)
            if nv < 1e-12:
                continue
            for sgn in (1.0, -1.0):
                y = sgn * v / nv
                if (Hn @ y >= -1e-10).all():
                    verts.append(y)
    V = np.unique(np.round(np.array(verts), 12), axis=0) if verts else np.zeros((0, 3))
    if len(V) == 0:
        return 0.0                         # >= 2 non-parallel planes and no feasible edge: empty (measure zero)
    if len(V) == 2:
        # a lune: all effective planes contain the edge line e; feasible arc in the circle perpendicular to e
        e = V[0]
        Q, _ = np.linalg.qr(np.c_[e, np.eye(3)]); B = Q[:, 1:3]
        Hp = Hn @ B
        t = (np.arange(1 << 20) + 0.5) * (2 * math.pi / (1 << 20))
        U = np.stack([np.cos(t), np.sin(t)], 1)
        frac = float(((U @ Hp.T) >= 0).all(1).mean())                    # arc fraction = theta / (2 pi)
        return frac                        # lune area 2 theta, theta = 2 pi frac; measure = 2 theta / (4 pi)
    if len(V) < 3:
        return 0.0                         # a single feasible ray: measure zero
    c = V.mean(0); c /= np.linalg.norm(c)
    e1 = V[0] - (V[0] @ c) * c; e1 /= np.linalg.norm(e1); e2 = np.cross(c, e1)
    ang = np.arctan2(V @ e2, V @ e1); V = V[np.argsort(ang)]
    om = 0.0
    for i in range(1, len(V) - 1):
        a, b, cc = V[0], V[i], V[i + 1]
        num = abs(a @ np.cross(b, cc)); den = 1 + a @ b + b @ cc + cc @ a
        om += 2 * math.atan2(num, den)
    return om / (4 * math.pi)


FIB = None


def solid_angle_grid(H, N=400000):
    global FIB
    if FIB is None:
        i = np.arange(N) + 0.5; phi = np.arccos(1 - 2 * i / N); th = math.pi * (1 + 5 ** 0.5) * i
        FIB = np.stack([np.cos(th) * np.sin(phi), np.sin(th) * np.sin(phi), np.cos(phi)], 1)
    return float(((FIB @ H.T) >= 0).all(1).mean())


def cone_first_moment(G):
    """E[x 1{G x >= 0}] for x ~ N(0, I_4)."""
    G = G[np.linalg.norm(G, axis=1) > 1e-12]
    G = G / np.linalg.norm(G, axis=1, keepdims=True)
    u = []                                                    # positively parallel constraints are one facet
    for i in range(len(G)):
        if all(np.abs(G[i] - G[j]).max() > 1e-9 for j in u):
            u.append(i)
    G = G[u]
    out = np.zeros(4); flags = 0
    for j in range(len(G)):
        g = G[j] / np.linalg.norm(G[j])
        # orthonormal basis of g^perp
        Q, _ = np.linalg.qr(np.c_[g, np.eye(4)])
        B = Q[:, 1:4]
        H = np.delete(G, j, 0) @ B
        p = solid_angle_cone3(H)
        if p < 0:
            p = solid_angle_grid(H); flags += 1
        out += g * p
    return out / math.sqrt(2 * math.pi), flags


if args.selftest:
    rs = np.random.RandomState(0); X = rs.standard_normal((1 << 22, 4))
    for t in range(6):
        G = rs.standard_normal((rs.randint(1, 7), 4))
        ex, fl = cone_first_moment(G)
        mc = (X * ((X @ G.T) >= 0).all(1)[:, None]).mean(0)
        print('cone', t, 'rows', len(G), 'exact', np.round(ex, 5), 'MC', np.round(mc, 5), 'flags', fl)
    sys.exit(0)

t0 = time.time()
W = [w.double().numpy() for w in ar.weights(seed, n, L)]
rng = np.random.RandomState(seed)


def fwd_pat(X):
    h = X; pats = []
    for l in range(L):
        z = h @ W[l].T; pats.append(z > 0); h = np.maximum(z, 0)
    return h, np.concatenate(pats, 1)


NT = 1 << args.log2train
Xtr = rng.standard_normal((NT, n)); Ftr, Ptr = fwd_pat(Xtr)
keys, inv, cnt = np.unique(np.packbits(Ptr, axis=1), axis=0, return_inverse=True, return_counts=True)
# held-out coverage of the seen patterns
Xho = np.random.RandomState(seed + 1).standard_normal((NT, n)); _, Pho = fwd_pat(Xho)
seen = set(map(bytes, keys)); ho_cov = float(np.mean([bytes(k) in seen for k in np.packbits(Pho, axis=1)]))
est = np.zeros(n); flags = 0
for ci in range(len(keys)):
    pat = Ptr[np.argmax(inv == ci)].reshape(L, n)
    M = np.eye(n); rows = []
    for l in range(L):
        Gl = W[l] @ M                                                   # pre-activation functionals of layer l
        rows.append(np.where(pat[l][:, None], Gl, -Gl))
        M = pat[l][:, None] * Gl
    m1, fl = cone_first_moment(np.concatenate(rows)); flags += fl
    est += M @ m1                                                       # A_P E[x 1_P], A_P = D_L G_L
# truth: average of 4 independently scrambled Sobol runs of 2^(log2truth - 2) points each (RQMC); truth noise =
# variance of that average estimated from the 4 replicates. VF from plain MC on 2^22 paths.
reps = []
for r_ in range(4):
    eng = qmc.Sobol(d=n, scramble=True, seed=seed * 1009 + 77 + r_); acc = np.zeros(n); NR = 1 << (args.log2truth - 2)
    for _ in range(max(1, NR >> 22)):
        F, _ = fwd_pat(ndtri(np.clip(eng.random(min(NR, 1 << 22)), 1e-15, 1 - 1e-15))); acc += F.sum(0)
    reps.append(acc / NR)
reps = np.array(reps); m0 = reps.mean(0)
Fv, _ = fwd_pat(np.random.RandomState(seed + 4242).standard_normal((1 << 22, n))); tr0 = float(Fv.var(0).sum())
truth_noise = float(reps.var(0, ddof=1).sum() / 4 / tr0)
VF = tr0
e_exact = float(((est - m0) ** 2).sum() / VF)
mc_adv = 1.0 / NT; e_mean_adv = float(((Ftr.mean(0) - m0) ** 2).sum() / VF)
rq = []
for r_ in range(4):
    eng = qmc.Sobol(d=n, scramble=True, seed=seed * 31 + r_)
    F, _ = fwd_pat(ndtri(np.clip(eng.random(NT), 1e-12, 1 - 1e-12))); rq.append(float(((F.mean(0) - m0) ** 2).sum() / VF))
res = dict(seed=seed, n=n, L=L, NT=NT, cells=int(len(keys)), heldout_coverage=ho_cov, grid_fallbacks=flags,
           err_exact=e_exact, truth_noise=truth_noise, mc_adv=mc_adv, mean_of_advice=e_mean_adv, rqmc_adv=float(np.mean(rq)),
           est=est.tolist(), truth=m0.tolist(), secs=time.time() - t0)
print(json.dumps(res))
out = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs', f'exact_cells_n{n}_L{L}_s{seed}.json')
json.dump(res, open(out, 'w'))
