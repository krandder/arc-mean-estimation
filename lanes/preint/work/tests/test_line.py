"""Tests for lib/line.py (exact line + radius integration through bias-free ReLU nets). Run: python tests/test_line.py"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import line as LN  # noqa: E402


def make_net(seed, dims):
    rng = np.random.default_rng(seed)
    return [rng.standard_normal((dims[i + 1], dims[i])) * math.sqrt(2.0 / dims[i]) for i in range(len(dims) - 1)]


def fwd(Ws, X):
    h = X
    for W in Ws:
        h = np.maximum(h @ W.T, 0.0)
    return h


def pattern(Ws, X):
    h = X
    pats = []
    for W in Ws:
        z = h @ W.T
        pats.append(z > 0)
        h = np.maximum(z, 0.0)
    return np.concatenate(pats, axis=1)


def brute_student(Ws, yhat, u, k, G=400001):
    """int f(yhat + s u) w_k(s) ds = k/sqrt(2 pi) int f(e(psi)) cos^(k-1) psi dpsi, trapezoid on a fine grid."""
    psi = np.linspace(-math.pi / 2, math.pi / 2, G)
    E = np.cos(psi)[:, None] * yhat[None, :] + np.sin(psi)[:, None] * u[None, :]
    F = fwd(Ws, E)
    wts = k / math.sqrt(2 * math.pi) * np.cos(psi) ** (k - 1)
    g = F * wts[:, None]
    h = psi[1] - psi[0]
    return h * (g.sum(0) - 0.5 * (g[0] + g[-1]))


def brute_gauss(Ws, y, u, G=400001, T=12.0):
    t = np.linspace(-T, T, G)
    X = y[None, :] + t[:, None] * u[None, :]
    F = fwd(Ws, X)
    g = F * (np.exp(-0.5 * t * t) / math.sqrt(2 * math.pi))[:, None]
    h = t[1] - t[0]
    return h * (g.sum(0) - 0.5 * (g[0] + g[-1]))


def test_single_lines():
    worst = 0.0
    for seed, dims in [(1, [4, 5, 5, 3]), (2, [6, 6, 6, 6, 6, 6]), (3, [3, 8, 8, 8, 2]), (4, [8] * 9)]:
        Ws = make_net(seed, dims)
        d = dims[0]
        rng = np.random.default_rng(100 + seed)
        u = rng.standard_normal(d)
        u /= np.linalg.norm(u)
        B = LN.orth_basis(u)
        Y = LN.bases_from_uniform(rng.random((4, d - 1)), B, normalise=True)
        wt = LN.Weight('student', d - 1)
        I, fl, cnt = LN.line_integrals(Ws, Y, u, wt)
        for i in range(Y.shape[0]):
            ref = brute_student(Ws, Y[i], u, d - 1)
            err = np.abs(I[i] - ref).max() / max(1e-12, np.abs(ref).max())
            worst = max(worst, err)
        Yg = LN.bases_from_uniform(rng.random((3, d - 1)), B, normalise=False)
        wg = LN.Weight('gauss')
        Ig, _, _ = LN.line_integrals(Ws, Yg, u, wg)
        for i in range(Yg.shape[0]):
            ref = brute_gauss(Ws, Yg[i], u)
            err = np.abs(Ig[i] - ref).max() / max(1e-12, np.abs(ref).max())
            worst = max(worst, err)
    print('single lines vs fine-grid quadrature: worst relative error %.2e' % worst)
    assert worst < 1e-6, worst


def test_window_mode():
    """Window mode (exact on |s| <= s0, one-point tail estimate) agrees with full mode to the tail's size, and the
    tail estimate is unbiased (checked with a large eps)."""
    Ws = make_net(5, [8] * 7)
    d = 8
    rng = np.random.default_rng(6)
    u = rng.standard_normal(d)
    u /= np.linalg.norm(u)
    B = LN.orth_basis(u)
    Y = LN.bases_from_uniform(rng.random((32, d - 1)), B)
    wt = LN.Weight('student', d - 1)
    Ifull, flf, cf = LN.line_integrals(Ws, Y, u, wt)
    Iw, flw, cw = LN.line_integrals(Ws, Y, u, wt, eps=1e-10, rng=rng)
    rel = np.abs(Iw - Ifull).max() / np.abs(Ifull).max()
    # unbiasedness of the tail estimate: eps = 0.3, average over many tail draws for one line
    reps = [LN.line_integrals(Ws, Y[:1], u, wt, eps=0.3, rng=rng)[0][0] for _ in range(4000)]
    reps = np.array(reps)
    z = (reps.mean(0) - Ifull[0]) / (reps.std(0, ddof=1) / math.sqrt(len(reps)) + 1e-300)
    live = reps.std(0) > 0
    print('window eps=1e-10: max rel diff to full %.1e (vertices %.0f vs %.0f); eps=0.3 tail draws: max |z| %.2f' % (
        rel, cw[:, -1].mean(), cf[:, -1].mean(), np.abs(z[live]).max()))
    assert rel < 1e-7 and np.abs(z[live]).max() < 4.5


def test_pieces_constant_pattern():
    """Between consecutive vertices the full activation pattern is constant (checked at 3 interior points)."""
    Ws = make_net(7, [6, 7, 7, 7, 7, 7])
    d = 6
    rng = np.random.default_rng(8)
    u = rng.standard_normal(d)
    u /= np.linalg.norm(u)
    B = LN.orth_basis(u)
    Y = LN.bases_from_uniform(rng.random((5, d - 1)), B)
    V0 = np.array([[0.0, -1.0], [1.0, 0.0], [0.0, 1.0]])
    H, V, lid, counts, fl = LN._propagate(Ws, Y, u, V0)
    bad = 0
    total = 0
    for i in range(Y.shape[0]):
        Vi = V[lid == i]
        for a, b in zip(Vi[:-1], Vi[1:]):
            pts = []
            for lam in (0.2, 0.5, 0.8):
                c = (1 - lam) * a + lam * b
                pts.append(c[0] * Y[i] + c[1] * u)
            P = pattern(Ws, np.array(pts))
            total += 1
            if not (P == P[1]).all():
                bad += 1
        assert np.all(np.diff(np.arctan2(Vi[:, 1], Vi[:, 0])) > 0)
    print('pieces checked %d, pattern not constant in %d' % (total, bad))
    assert bad == 0


def test_depth1_unbiased():
    """E relu(w.x) = |w| / sqrt(2 pi): the average of line integrals over uniform yhat is unbiased."""
    d, n = 5, 7
    Ws = make_net(11, [d, n])
    truth = np.linalg.norm(Ws[0], axis=1) / math.sqrt(2 * math.pi)
    rng = np.random.default_rng(12)
    u = rng.standard_normal(d)
    u /= np.linalg.norm(u)
    B = LN.orth_basis(u)
    m = 1 << 14
    Y = LN.bases_from_uniform(rng.random((m, d - 1)), B)
    I, _, _ = LN.line_integrals(Ws, Y, u, LN.Weight('student', d - 1), chunk=4096)
    est = I.mean(0)
    se = I.std(0, ddof=1) / math.sqrt(m)
    z = (est - truth) / se
    print('depth 1: max |z| = %.2f (n = %d units), per-line variance / plain variance %.3f' % (
        np.abs(z).max(), n, (I.var(0).sum() / (np.maximum(rng.standard_normal((1 << 14, d)) @ Ws[0].T, 0).var(0).sum()))))
    assert np.abs(z).max() < 4.5


def test_deep_vs_mc():
    d = 6
    Ws = make_net(21, [d] + [6] * 10)
    rng = np.random.default_rng(22)
    X = rng.standard_normal((1 << 21, d))
    F = fwd(Ws, X)
    mc = F.mean(0)
    mcse = F.std(0) / math.sqrt(X.shape[0])
    u = rng.standard_normal(d)
    u /= np.linalg.norm(u)
    B = LN.orth_basis(u)
    m = 1 << 13
    Y = LN.bases_from_uniform(rng.random((m, d - 1)), B)
    I, fl, cnt = LN.line_integrals(Ws, Y, u, LN.Weight('student', d - 1), chunk=1024)
    est = I.mean(0)
    se = I.std(0, ddof=1) / math.sqrt(m)
    live = (se > 0) | (mcse > 0)
    z = (est - mc)[live] / np.sqrt(se ** 2 + mcse ** 2)[live]
    print('live units %d of %d' % (live.sum(), live.size))
    print('deep 6x10: max |z| vs 2^21-path MC = %.2f; mean interior vertices per line %.1f; cost %.1f passes/line' % (
        np.abs(z).max(), cnt[:, -1].mean(), fl.mean() / (2 * 36 * 10)))
    assert np.abs(z).max() < 4.5


def test_chunk_invariance():
    """Processing lines in chunks of different sizes gives the same integrals and the same per-line FLOP counts."""
    Ws = make_net(31, [8] * 7)
    d = 8
    rng = np.random.default_rng(32)
    u = rng.standard_normal(d)
    u /= np.linalg.norm(u)
    Y = LN.bases_from_uniform(rng.random((37, d - 1)), LN.orth_basis(u))
    wt = LN.Weight('student', d - 1)
    I1, f1, c1 = LN.line_integrals(Ws, Y, u, wt, chunk=1)
    I2, f2, c2 = LN.line_integrals(Ws, Y, u, wt, chunk=37)
    I3, f3, c3 = LN.line_integrals(Ws, Y, u, wt, chunk=5)
    err = max(np.abs(I1 - I2).max(), np.abs(I1 - I3).max()) / np.abs(I1).max()
    print('chunk invariance: max rel diff %.1e; flops equal %s; counts equal %s' % (
        err, np.allclose(f1, f2) and np.allclose(f1, f3), (c1 == c2).all() and (c1 == c3).all()))
    assert err < 1e-12 and np.allclose(f1, f2) and np.allclose(f1, f3) and (c1 == c2).all()


def test_tail_map_linearity():
    """With a linear tail map J the line integral equals J times the line integral of the cut net."""
    Ws = make_net(41, [6] * 5)
    d = 6
    rng = np.random.default_rng(42)
    J = rng.standard_normal((3, 6))
    u = rng.standard_normal(d)
    u /= np.linalg.norm(u)
    Y = LN.bases_from_uniform(rng.random((9, d - 1)), LN.orth_basis(u))
    wt = LN.Weight('student', d - 1)
    IJ, _, _ = LN.line_integrals(Ws, Y, u, wt, J=J)
    I, _, _ = LN.line_integrals(Ws, Y, u, wt)
    err = np.abs(IJ - I @ J.T).max() / np.abs(IJ).max()
    print('tail map: max rel diff %.1e' % err)
    assert err < 1e-12


def test_coincident_roots():
    """Units whose pre-activations vanish at the same point (identical rows, positive multiples) are handled."""
    rng = np.random.default_rng(51)
    W1 = rng.standard_normal((6, 5))
    W1[1] = W1[0]                       # identical rows
    W1[2] = 2.5 * W1[0]                 # positive multiple
    W1[3] = -W1[0]                      # negative multiple (same zero set)
    Ws = [W1, rng.standard_normal((4, 6)) * 0.6, rng.standard_normal((3, 4)) * 0.7]
    d = 5
    u = rng.standard_normal(d)
    u /= np.linalg.norm(u)
    Y = LN.bases_from_uniform(rng.random((3, d - 1)), LN.orth_basis(u))
    I, _, _ = LN.line_integrals(Ws, Y, u, LN.Weight('student', d - 1))
    worst = max(np.abs(I[i] - brute_student(Ws, Y[i], u, d - 1)).max() / max(1e-12, np.abs(I[i]).max())
                for i in range(3))
    print('coincident roots: worst relative error vs quadrature %.1e' % worst)
    assert worst < 1e-6


def test_flop_counter():
    """The per-line FLOP count equals the nominal model recomputed from the vertex counts (one line, full mode)."""
    Ws = make_net(61, [5, 7, 6, 4])
    d = 5
    rng = np.random.default_rng(62)
    u = rng.standard_normal(d)
    u /= np.linalg.norm(u)
    Y = LN.bases_from_uniform(rng.random((1, d - 1)), LN.orth_basis(u))
    wt = LN.Weight('student', d - 1)
    I, fl, cnt = LN.line_integrals(Ws, Y, u, wt)
    exp = 0.0
    for li, W in enumerate(Ws):
        nout, nin = W.shape
        Vb, Va = cnt[0, li], cnt[0, li + 1]
        C = Va - Vb
        exp += Vb * nout * (2 * nin - 1) + (Vb - 1) * 2 * nout + C * (3 * nout + 9) + Va * nout
    n_out = Ws[-1].shape[0]
    Vf = cnt[0, -1]
    exp += Vf * (n_out + 2 * wt.f_cdf + LN.F_POW + 4)          # per-vertex integration charge
    exp += (Vf - 3) * (4 * n_out + 8)                          # finite pieces (rays are the two end pieces)
    print('flop counter: reported %.0f, recomputed %.0f' % (fl[0], exp))
    assert abs(fl[0] - exp) < 1e-6 * exp


if __name__ == '__main__':
    test_single_lines()
    test_window_mode()
    test_pieces_constant_pattern()
    test_depth1_unbiased()
    test_deep_vs_mc()
    test_chunk_invariance()
    test_tail_map_linearity()
    test_coincident_roots()
    test_flop_counter()
    print('all tests passed')
