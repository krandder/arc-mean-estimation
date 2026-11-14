"""Tests for lib/rel.py. Run: OPENBLAS_NUM_THREADS=1 python tests/test_rel.py"""
import math
import sys

import numpy as np

sys.path.insert(0, '/home/agent/workspaces/mats/work/relevance/lib')
import rel  # noqa: E402

FAILS = []


def check(name, cond, info=''):
    print(('PASS ' if cond else 'FAIL ') + name + ('  ' + str(info) if info else ''))
    if not cond:
        FAILS.append(name)


def test_forward_and_noise_sharing():
    rng = np.random.default_rng(0)
    n, t = 16, 5
    Ws = [rng.standard_normal((n, n)) * math.sqrt(2 / n) for _ in range(t)]
    f0 = rel.Future(Ws, 0.0)
    X = rng.standard_normal((7, n))
    h = X
    for W in Ws:
        h = np.maximum(h @ W.T, 0)
    check('forward sigma=0 matches manual', np.allclose(f0.forward(X[None])[0], h))
    f1 = rel.Future(Ws, 1.0)
    a = f1.forward(np.stack([X, X, X]), np.random.default_rng(1), share=[0, 0, 1])
    check('shared stream gives identical outputs', np.allclose(a[0], a[1]))
    check('independent stream differs', not np.allclose(a[0], a[2]))
    # stationary future/cloud consistency with st.run_window (same weights)
    fut = rel.stationary_future(1234, 8, 3)
    check('stationary future has s+1 layers', fut.t == 4 and fut.sigma == 1.0)
    W1 = rel.st.W_layer(1234, 8, 1)
    check('stationary future ends with the output layer W_1', np.allclose(fut.Ws[-1], W1))


def test_jvp_vjp():
    rng = np.random.default_rng(2)
    n, t = 12, 6
    Ws = [rng.standard_normal((n, n)) * math.sqrt(2 / n) for _ in range(t)]
    for sigma in [0.0, 1.0]:
        f = rel.Future(Ws, sigma)
        X = rng.standard_normal((5, n)) * 3
        V = rng.standard_normal((5, n))
        eps = 1e-6
        ap = f.forward((X + eps * V)[None], np.random.default_rng(9))[0]
        am = f.forward((X - eps * V)[None], np.random.default_rng(9))[0]
        _, jv = f.jvp(X[None], V[None], np.random.default_rng(9))
        check(f'jvp vs finite difference sigma={sigma}', np.allclose((ap - am) / (2 * eps), jv[0], atol=1e-6),
              np.abs((ap - am) / (2 * eps) - jv[0]).max())
        R = rng.standard_normal((5, n))
        _, u = f.vjp(X[None], R[None], np.random.default_rng(9))
        lhs = np.einsum('pi,pi->p', R, jv[0])
        rhs = np.einsum('pi,pi->p', u[0], V)
        check(f'vjp is the adjoint of jvp sigma={sigma}', np.allclose(lhs, rhs))
        # multi-tangent shapes
        VV = rng.standard_normal((1, 5, 3, n))
        _, jvv = f.jvp(X[None], VV, np.random.default_rng(9))
        _, jv0 = f.jvp(X[None], VV[:, :, 0, :], np.random.default_rng(9))
        check(f'multi-tangent jvp sigma={sigma}', np.allclose(jvv[:, :, 0, :], jv0))
        RR = rng.standard_normal((1, 5, 3, n))
        _, uu = f.vjp(X[None], RR, np.random.default_rng(9))
        _, u0 = f.vjp(X[None], RR[:, :, 1, :], np.random.default_rng(9))
        check(f'multi-cotangent vjp sigma={sigma}', np.allclose(uu[:, :, 1, :], u0))


def test_decompose_identity():
    rng = np.random.default_rng(3)
    n, t = 16, 8
    Ws = [rng.standard_normal((n, n)) * math.sqrt(2 / n) for _ in range(t)]
    for sigma in [0.0, 1.0]:
        f = rel.Future(Ws, sigma)
        m = np.abs(rng.standard_normal(n)) * 2
        X = m + rng.standard_normal((50, n)) * 0.8
        r = f.decompose(X, m, np.random.default_rng(5))
        # rebuild the exact recursion delta_k = D(m) W delta_{k-1} + |z_x| 1[flip], with the same noise
        g = np.random.default_rng(5)
        hx, hm, d = X.copy(), np.broadcast_to(m, X.shape).copy(), X - m
        for k in range(t):
            zx, zm = hx @ Ws[k].T, hm @ Ws[k].T
            dm = zm > 0
            d = (d @ Ws[k].T) * dm + np.abs(zx) * ((zx > 0) != dm)
            hx, hm = np.maximum(zx, 0), np.maximum(zm, 0)
            if k < t - 1 and sigma > 0:
                xi = g.standard_normal(hx.shape)
                hx, hm = hx + xi, hm + xi
        check(f'exact identity a(x)-a(m) = recursion sigma={sigma}', np.allclose(d, r['da'], atol=1e-10),
              np.abs(d - r['da']).max())
        # vanishing perturbation: no flips, all parts agree
        Xs = m + rng.standard_normal((20, n)) * 1e-9
        r2 = f.decompose(Xs, m, np.random.default_rng(6))
        check(f'tiny perturbation: lin == fo == da sigma={sigma}',
              np.allclose(r2['lin'], r2['da'], atol=1e-14) and np.allclose(r2['fo'], r2['da'], atol=1e-14))


def test_ustat():
    rng = np.random.default_rng(4)
    n, no = 20, 6
    B = rng.standard_normal((no, n)) * 0.3
    vals = []
    for rep in range(200):
        Z = rng.standard_normal((400, n))
        a = Z @ B.T + rng.standard_normal((400, no)) * 2 + (Z[:, :1] ** 2)
        U, se, _ = rel.ustat_sq(a - a.mean(0), Z)
        vals.append(U)
    vals = np.array(vals)
    target = np.sum(B * B)
    z = (vals.mean() - target) / (vals.std(ddof=1) / math.sqrt(len(vals)))
    check('U-statistic unbiased for |E[a Z^T]|^2', abs(z) < 4, f'mean {vals.mean():.4f} target {target:.4f} z {z:.2f}')
    check('U-statistic jackknife SE in the right range', 0.5 < se / vals.std(ddof=1) < 2.0,
          f'se {se:.4f} sd {vals.std(ddof=1):.4f}')


class LinFut:
    """Linear test future g(X) = A X (sigma = 0) with the Future interface used by the estimators."""

    def __init__(self, A, quad=None):
        self.A, self.sigma, self.quad = A, 0.0, quad
        self.Ws = [A]

    def forward(self, X, rng=None, share=None):
        X = X if X.ndim == 3 else X[None]
        out = X @ self.A.T
        if self.quad is not None:
            u, c = self.quad
            out = out + c * ((X @ u) ** 2)[..., None] * np.ones(self.A.shape[0])
        return out


def test_residuals_linear():
    rng = np.random.default_rng(7)
    n, no = 10, 4
    A = rng.standard_normal((no, n))
    Xs = rng.standard_normal((20000, n)) @ np.diag(np.linspace(0.3, 2.0, n)) + 1.0
    fr = rel.gaussian_frame(Xs)
    M = fr['S12'] @ A.T @ A @ fr['S12']
    w, U = np.linalg.eigh(M)
    w, U = w[::-1], U[:, ::-1]
    lf = LinFut(A)
    res = rel.subspace_residuals(lf, fr, U, [0, 1, 2, 3, 4], 40000, rng, true_X=Xs[:20000])
    ok = True
    info = []
    for k in [0, 1, 2, 3, 4]:
        pred = w[k:].sum()
        r, se = res['gauss'][k]
        info.append((k, round(r, 3), round(pred, 3)))
        ok &= abs(r - pred) < 4 * se + 1e-9
        rt, set_ = res['true'][k]
        ok &= abs(rt - pred) < 4 * set_ + 1e-9 + 0.02 * pred
    check('linear future: Gaussian and true-law residuals = eigenvalue tails', ok, info)


def test_mehler_quadratic():
    rng = np.random.default_rng(8)
    n = 6
    A = np.zeros((1, n))
    A[0, 0] = 1.0
    u = np.zeros(n)
    u[1] = 1.0
    lf = LinFut(A, quad=(u, 0.5))
    X = rng.standard_normal((50000, n))
    fr = rel.gaussian_frame(X)
    # g = Z0 + 0.5 Z1^2 (approximately, frame is estimated): V1 = 1, V2 = 0.25 * 2 = 0.5
    cur = rel.mehler_curve(lf, fr, [0.0, 0.5, 0.9], 100000, rng)
    pred = {r: (1 - r) * 1.0 + (1 - r * r) * 0.5 for r in [0.0, 0.5, 0.9]}
    ok = all(abs(cur[r][0] - pred[r]) < 4 * cur[r][1] + 0.01 for r in pred)
    check('Mehler curve of Z0 + Z1^2/2', ok, {r: (round(cur[r][0], 3), round(pred[r], 3)) for r in pred})
    Z = (X - fr['m']) @ fr['Sm12']
    V1, se, _ = rel.stein_linear(lf, X, Z, rng)
    check('Stein V1 of Z0 + Z1^2/2 is 1', abs(V1 - 1.0) < 4 * se + 0.01, (V1, se))


def test_active_subspace_poincare():
    rng = np.random.default_rng(10)
    n, t = 10, 4
    Ws = [rng.standard_normal((n, n)) * math.sqrt(2 / n) for _ in range(t)]
    f = rel.Future(Ws, 0.0)
    Xs = np.abs(rng.standard_normal(n)) * 3 + rng.standard_normal((20000, n))
    fr = rel.gaussian_frame(Xs)
    C, w, U = rel.active_subspace(f, fr, 20000, rng)
    J1, se = rel.gradient_energy(f, fr, 20000, rng)
    check('trace of active-subspace matrix = gradient energy', abs(np.trace(C) - J1) < 4 * se + 0.03 * J1,
          (np.trace(C), J1))
    res = rel.subspace_residuals(f, fr, U, [0, 2, 5], 20000, rng)
    ok = all(res['gauss'][k][0] <= w[k:].sum() * 1.05 + 3 * res['gauss'][k][1] for k in [0, 2, 5])
    check('Poincare: residual(top-k AS) <= tail of AS eigenvalues', ok,
          [(k, round(res['gauss'][k][0], 3), round(w[k:].sum(), 3)) for k in [0, 2, 5]])


if __name__ == '__main__':
    test_forward_and_noise_sharing()
    test_jvp_vjp()
    test_decompose_identity()
    test_ustat()
    test_residuals_linear()
    test_mehler_quadratic()
    test_active_subspace_poincare()
    print('FAILS:', FAILS)
    sys.exit(1 if FAILS else 0)
