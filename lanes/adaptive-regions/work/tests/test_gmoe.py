"""Tests for lib/gmoe.py (run: nice -n 19 python tests/test_gmoe.py)."""
import os, sys, math
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import gmoe  # noqa: E402

ok = True


def check(name, cond, info=''):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name + ('  ' + info if info else ''))
    ok = ok and bool(cond)


rng = np.random.RandomState(0)
# 1. linear Gaussian chain: K = 1 is exact up to sampling error
n = 5
A1 = rng.standard_normal((n, n)) / math.sqrt(n); A2 = rng.standard_normal((n, n)) / math.sqrt(n)
X = rng.standard_normal((40000, n)); H1 = X @ A1.T + 0.3; H2 = H1 @ A2.T - 0.2
m1 = gmoe.LayerMoE(1).fit(X, H1); m2 = gmoe.LayerMoE(1).fit(H1, H2)
w, M, S = np.ones(1), np.zeros((1, n)), np.eye(n)[None]
w, M, S = m1.push(w, M, S); w, M, S = m2.push(w, M, S)
true_mean = A2 @ (0.3 * np.ones(n)) - 0.2
true_cov = A2 @ A1 @ A1.T @ A2.T
check('linear chain mean (K=1)', np.abs(M[0] - true_mean).max() < 0.02, f'{np.abs(M[0] - true_mean).max():.4f}')
check('linear chain covariance (K=1)', np.abs(S[0] - true_cov).max() < 0.03, f'{np.abs(S[0] - true_cov).max():.4f}')

# 2. one ReLU layer in 2 dimensions: propagated mean approaches E relu(W x) as K grows
W = rng.standard_normal((2, 2))
X = rng.standard_normal((40000, 2)); V = np.maximum(X @ W.T, 0)
exact = np.linalg.norm(W, axis=1) / math.sqrt(2 * math.pi)
errs = []
for K in (1, 4, 16):
    mdl = gmoe.LayerMoE(K, seed=1).fit(X, V)
    w, M, S = mdl.push(np.ones(1), np.zeros((1, 2)), np.eye(2)[None])
    est = (w[:, None] * M).sum(0) / w.sum()
    errs.append(float(np.abs(est - exact).max() / exact.max()))
check('one ReLU layer: relative mean error falls with K', errs[-1] < errs[0], str(np.round(errs, 4)))
check('one ReLU layer: K=16 within 5%', errs[-1] < 0.05, f'{errs[-1]:.4f}')

# 3. conditional-mean prediction is the GMR formula (K = 1 reduces to linear regression)
mdl = gmoe.LayerMoE(1).fit(X, V)
pred = mdl.predict_mean(X[:1000])
B, *_ = np.linalg.lstsq(np.c_[X, np.ones(len(X))], V, rcond=None)
lin = np.c_[X[:1000], np.ones(1000)] @ B
check('K=1 conditional mean = least squares', np.abs(pred - lin).max() < 1e-3, f'{np.abs(pred - lin).max():.2e}')
print('ALL PASS' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
