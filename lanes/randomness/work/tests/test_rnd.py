"""Tests for lib/rnd.py (run: python tests/test_rnd.py). Each check prints OK or raises."""
import math
import os
import sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))
import rnd  # noqa: E402

rng = np.random.default_rng(1)


def close(a, b, tol, what):
    if not np.all(np.abs(np.asarray(a) - np.asarray(b)) <= tol):
        raise AssertionError(f'{what}: {a} vs {b}')
    print('OK', what)


# Gegenbauer polynomials: closed forms and orthogonality under the (1 - t^2)^{(n-3)/2} weight
n = 16
t = np.linspace(-1, 1, 7)
close(rnd.gegen_P(2, n, t), (n * t ** 2 - 1) / (n - 1), 1e-12, 'P2 closed form')
close(rnd.gegen_P(3, n, t), ((n + 2) * t ** 3 - 3 * t) / (n - 1), 1e-12, 'P3 closed form')
tt = np.cos(np.linspace(0, math.pi, 200001))
w = (1 - tt ** 2) ** ((n - 3) / 2)
dth = math.pi / 200000
ip = np.sum(rnd.gegen_P(3, n, tt) * rnd.gegen_P(5, n, tt) * w * np.sqrt(1 - tt ** 2)) * dth
close(ip, 0.0, 1e-6, 'P3 _|_ P5')

# aliasing: MC-like identities and design strengths
for n in (8, 32):
    S = rnd.simplex_base(n)
    close(np.linalg.norm(S, axis=1), 1.0, 1e-12, f'simplex unit n={n}')
    G = S @ S.T
    close(G[~np.eye(n + 1, dtype=bool)], -1.0 / n, 1e-12, f'simplex inner products n={n}')
    A = rnd.aliasing(S, 4)
    close(A[1:3], 0.0, 1e-12, f'simplex is a 2-design n={n}')
    Q = rnd.haar(n, rng)
    close(rnd.aliasing(rnd.rotate(S, Q), 4), A, 1e-10, f'aliasing rotation invariant n={n}')
    C = rnd.cross_base(n)
    A = rnd.aliasing(C, 5)
    close(A[1:4], 0.0, 1e-12, f'cross-polytope is a 3-design n={n}')
    close(A[5], 0.0, 1e-12, f'cross-polytope kills degree 5 (antipodal) n={n}')
    B = rnd.d_onb(n, rng)
    A = rnd.aliasing(B, 3)
    close(A[2], 0.0, 1e-12, f'orthonormal basis kills degree 2 n={n}')
    close(A[3], 1.0 / n, 1e-12, f'orthonormal basis A_3 = 1/n n={n}')
    AP = rnd.d_anti(64, n, rng)
    A = rnd.aliasing(AP, 3)
    close(A[[1, 3]], 0.0, 1e-12, f'antipodal kills odd degrees n={n}')
Q = rnd.haar(5, rng)
close(Q @ Q.T, np.eye(5), 1e-12, 'haar orthogonal')

# Kerdock (n = 256): unit vectors, inner products in {0, +-1/16} across bases, design strength from one row profile
B = rnd.kerdock_bases(256)
V = B.reshape(-1, 256)
close(np.linalg.norm(V[:1000], axis=1), 1.0, 1e-12, 'kerdock unit')
g = V[[0, 300, 5000, 33000]] @ V.T
vals = np.unique(np.round(np.abs(g), 9))
close(len(vals), 3, 0, f'kerdock |inner products| in {{0, 1/16, 1}}: {vals}')
m_full = 2 * V.shape[0]
for row in range(4):
    gi = g[row]
    gi = np.concatenate([gi, -gi])                       # antipodal set
    for d in range(1, 6):
        Ad = rnd.gegen_P(d, 256, gi).sum() / m_full
        if abs(Ad) > 1e-9:
            raise AssertionError(f'kerdock A_{d} row {row} = {Ad}')
print('OK kerdock antipodal set is a 5-design (row profiles)')
for row in range(4):
    gi = g[row]
    for d in (2, 4):
        Ad = rnd.gegen_P(d, 256, gi).sum() / V.shape[0]
        if abs(Ad) > 1e-9:
            raise AssertionError(f'MUB A_{d} row {row} = {Ad}')
print('OK MUB vectors (no antipodes) kill degrees 2 and 4 (row profiles)')

# k-wise independent discretised Gaussians: exact moments
n, q = 6, 7
X = rnd.kwise_gauss(2, n, q)
close(X.shape[0], q ** 2, 0, 'kwise size q^k')
close(X.mean(0), 0.0, 1e-12, 'kwise k=2 mean zero')
close(X.T @ X / X.shape[0], np.eye(n), 1e-12, 'kwise k=2 covariance identity')
X3 = rnd.kwise_gauss(3, n, q)
m3 = np.einsum('ia,ib,ic->abc', X3, X3, X3) / X3.shape[0]
close(m3, 0.0, 1e-12, 'kwise k=3 third moments vanish')
m2 = X3.T @ X3 / X3.shape[0]
close(m2, np.eye(n), 1e-12, 'kwise k=3 covariance identity')
# pairwise joint law uniform on the q^2 grid
V2 = np.round(X[:, [1, 4]], 12)
_, cnt = np.unique(V2, axis=0, return_counts=True)
close(len(cnt), q * q, 0, 'kwise pairs cover the grid')
close(cnt, 1, 0, 'kwise pairs uniform')

# lattice and Sobol points in (0, 1)
P = rnd.lattice_unit(1024, 16)
assert P.min() > 0 and P.max() < 1
P = rnd.sobol_unit(10, 16, scramble=False)
assert P.min() > 0 and P.max() < 1
close(np.sort(P[:, 0]), (np.arange(1024) + 0.5) / 1024, 1e-12, 'centred Sobol 1D projection stratified')
print('OK unit-cube point sets')

# gate-aligned bases
W1 = rng.standard_normal((32, 32)) * math.sqrt(2 / 32)
Qp = rnd.basis_polar(W1)
close(Qp @ Qp.T, np.eye(32), 1e-10, 'polar basis orthogonal')
U, S, Vt = np.linalg.svd(W1)
close((U * S) @ U.T @ Qp, W1, 1e-10, 'W1 = (W1 W1^T)^{1/2} Q')
Qs = rnd.basis_svd(W1)
x = rng.standard_normal(32)
s = Qs @ x
close(np.sum((W1 @ x) ** 2), np.sum(S ** 2 * s ** 2), 1e-10, 'svd basis diagonalises |W1 x|^2')

# nets and truths
net = rnd.Net(300, 32, 4)
tr = rnd.load_truth(300, 32, 4)
X = rng.standard_normal((4, 32))
h = X.copy()
for w in net.W64:
    h = np.maximum(h @ w.numpy().T, 0.0)
close(net.outs(X), h, 1e-4, 'float32 forward matches float64')
est = rnd.plain_estimate(net, rng.standard_normal((1 << 16, 32)))
e = rnd.nmse(est, tr)
assert e < 50.0 / (1 << 16), e
print('OK ladder truth loads; MC nMSE at 2^16 =', e, 'x N =', e * (1 << 16))
tr = rnd.load_truth(200, 256, 32)
assert tr is not None and tr['V'] > 0
print('OK 256 x 32 truth loads; V =', tr['V'], 'floor', tr['floor'])
print('ALL OK')

# moment-matched k-wise levels: degree-4 and degree-6 moments exact
for k_, q_ in ((4, 37), (6, 67)):
    lev = rnd.kwise_levels(q_, k_)
    close([np.mean(lev ** 2), np.mean(lev ** 4)] + ([np.mean(lev ** 6)] if k_ >= 6 else []),
          [1.0, 3.0] + ([15.0] if k_ >= 6 else []), 1e-9, f'kwise levels k={k_} q={q_} match Gaussian moments')
X4 = rnd.kwise_gauss(4, 5, 7)
m4 = np.einsum('ia,ib,ic,id->abcd', X4, X4, X4, X4) / X4.shape[0]
import itertools
ok = True
for a_, b_, c_, d_ in itertools.product(range(5), repeat=4):
    idx = sorted([a_, b_, c_, d_])
    cnts = [idx.count(v) for v in set(idx)]
    target = 0.0
    if all(cc % 2 == 0 for cc in cnts):
        target = 1.0
        for cc in cnts:
            target *= {2: 1.0, 4: 3.0}[cc]
    ok &= abs(m4[a_, b_, c_, d_] - target) < 1e-9
assert ok, 'kwise k=4 fourth moments'
print('OK kwise k=4 design matches all Gaussian moments of degree <= 4')
print('ALL OK (2)')
