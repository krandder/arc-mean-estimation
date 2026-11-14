"""Checks for lib/cubesphere.py (moments, certification, convergence on shallow nets)."""
import math
import sys

import numpy as np

sys.path.insert(0, '/home/agent/workspaces/mats/work/nd-exact/lib')
import cubesphere as cs  # noqa: E402
import ndx  # noqa: E402


def test_faces_sum():
    mo = cs.Moments()
    Ptot, mtot = 0.0, np.zeros(8)
    for i in range(8):
        for s in (1.0, -1.0):
            a = -np.ones(8)
            b = np.ones(8)
            a[i] = b[i] = 0.0
            P, m = mo.cone(i, s, a, b)
            assert abs(P - 1 / 16) < 1e-12, P
            Ptot += P
            mtot += m
    assert abs(Ptot - 1) < 1e-12
    assert np.abs(mtot).max() < 1e-12


def test_subcell_vs_mc():
    rng = np.random.default_rng(1)
    mo = cs.Moments()
    i, s = 2, -1.0
    a = -np.ones(8)
    b = np.ones(8)
    a[i] = b[i] = 0.0
    a[0], b[0] = -0.25, 0.5
    a[5], b[5] = 0.0, 0.125
    a[7], b[7] = -1.0, -0.5
    P, m = mo.cone(i, s, a, b)
    X = rng.standard_normal((1 << 22, 8))
    t = s * X[:, i]
    g = X / np.abs(X[:, [i]])
    ok = t > 0
    for j in range(8):
        if j != i:
            ok &= (g[:, j] >= a[j]) & (g[:, j] <= b[j])
    Pm = ok.mean()
    mm = (X * ok[:, None]).mean(0)
    se = math.sqrt(Pm / X.shape[0])
    assert abs(P - Pm) < 5 * se, (P, Pm, se)
    assert np.abs(m - mm).max() < 5 * math.sqrt(P * 2 / X.shape[0]), (m, mm)


def test_depth1_converges():
    """Depth 1 (E[relu(W x)] = |w_j| / sqrt(2 pi) exactly): the anytime error falls as cells are added
    (a correctness check, not a performance claim; the rate is measured in scratch/depth1_rate.py)."""
    Ws = ndx.make_weights(103)
    est = cs.CubeSphere(Ws, 1)
    est.start()
    exact = np.linalg.norm(Ws[0], axis=1) / math.sqrt(2 * math.pi)
    errs = []
    for target in (250, 1000, 4000):
        while est.n_cells < target and est.refine_one():
            pass
        errs.append(np.abs(est.estimate() - exact).max() / exact.max())
    print('depth1 rel err at 250/1000/4000 cells', errs, 'certified mass', est.P_res)
    assert errs[2] < errs[1] < errs[0]


def test_certified_cells_are_linear():
    """On certified cells, sampled points have one activation pattern and f_c = A x."""
    Ws = ndx.make_weights(111)
    c = 6
    est = cs.CubeSphere(Ws, c)
    # take a small cell and certify by brute force sampling
    i, s = 0, 1.0
    rng = np.random.default_rng(3)
    found = 0
    for trial in range(400):
        a = -np.ones(8)
        b = np.ones(8)
        a[i] = b[i] = 0.0
        for j in range(1, 8):
            lo = rng.integers(0, 64)
            a[j] = -1 + lo / 32
            b[j] = a[j] + 1 / 32
        ks, A, M, strad = est._test(i, s, a, b, 0, np.eye(8))
        if ks is None:
            found += 1
            g = a + (b - a) * rng.random((2000, 8))
            g[:, i] = s
            X = g * rng.exponential(1.0, (2000, 1))
            h, pat = ndx.fwd_patterns(Ws, X, 0, c)
            assert len({p.tobytes() for p in pat}) == 1
            assert np.allclose(h, X @ A.T, rtol=1e-10, atol=1e-14)
    print('certified cells found', found)
    assert found > 0




def test_quadrature_order():
    """Q = 32 and Q = 64 agree with Q = 160 on random dyadic cells (relative to the face mass)."""
    rng = np.random.default_rng(7)
    ref = cs.Moments(Q=160)
    worst = {32: 0.0, 64: 0.0}
    for trial in range(200):
        i = int(rng.integers(8))
        s = 1.0 if rng.random() < 0.5 else -1.0
        a = -np.ones(8)
        b = np.ones(8)
        for j in range(8):
            lev = int(rng.integers(0, 12))
            k = int(rng.integers(0, 2 ** lev))
            a[j] = -1 + 2 * k / 2 ** lev
            b[j] = a[j] + 2 / 2 ** lev
        a[i] = b[i] = 0.0
        P0, m0 = ref.cone(i, s, a, b)
        for Q in (32, 64):
            P, m = cs.Moments(Q=Q).cone(i, s, a, b)
            if P0 > 0:
                worst[Q] = max(worst[Q], abs(P - P0) / P0, np.abs(m - m0).max() / (np.abs(m0).max() + 1e-300))
    print('worst relative moment error', worst)
    assert worst[64] < 1e-10




def test_cs2_certified_cells_exact_full_depth():
    """cs2: on cells certified through the full net (pattern through c0 and image in K), f = J A x at sampled points."""
    import cs2
    Ws = ndx.make_weights(111)
    est = cs2.CS2(Ws, c0=32)
    est.setup()
    assert est.K is not None
    rng = np.random.default_rng(5)
    checked = 0
    for _ in range(3000):
        if not est.refine_one():
            break
    # re-derive a few certified cells by brute force: sample leaves from the heap's neighbours is not stored, so
    # test random small cells directly
    for trial in range(3000):
        i = int(rng.integers(8))
        s = 1.0 if rng.random() < 0.5 else -1.0
        a = -np.ones(8)
        b = np.ones(8)
        for j in range(8):
            k = int(rng.integers(0, 32))
            a[j] = -1 + k / 16
            b[j] = a[j] + 1 / 16
        a[i] = b[i] = 0.0
        val, cell = est._make(i, s, a, b, 0, np.eye(8), np.eye(8), 0)
        if cell is None and np.any(val != 0):
            g = a + (b - a) * rng.random((500, 8))
            g[:, i] = s
            X = g * rng.exponential(1.0, (500, 1))
            out = ndx.fwd(Ws, X)
            P, mom = est.mom.cone(i, s, a, b)
            # f is linear on the cell: out = B x with B = J A; recover B from val/P = B m and check a few points
            B = np.linalg.lstsq(X, out, rcond=None)[0].T
            assert np.allclose(out, X @ B.T, rtol=1e-8, atol=1e-12 * np.abs(out).max())
            assert np.allclose(val / P, B @ (mom / P), rtol=1e-8, atol=1e-12 * np.abs(out).max())
            checked += 1
            if checked >= 5:
                break
    print('cs2 certified cells checked', checked)
    assert checked >= 1


if __name__ == '__main__':
    for name, f in list(globals().items()):
        if name.startswith('test_'):
            f()
            print('ok', name)
