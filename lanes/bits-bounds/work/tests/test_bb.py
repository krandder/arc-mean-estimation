"""Tests for lib/bb.py, lib/chain3.py, lib/meanfield.py and the identities used in FORMAL.md. Run: python tests/test_bb.py"""
import os
import sys
import math
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))
import bb
import chain3
import meanfield


def test_euler_identity():
    """g_l(h) = J_l(h) h exactly (frozen propagation with h's own gates)."""
    W = bb.make_weights(1, 16, 12)
    rng = np.random.default_rng(0)
    X = rng.standard_normal((5, 16))
    for l in [0, 3, 7]:
        H = bb.forward(W, X, 0, l)
        for i in range(5):
            masks = bb.gate_path(W, H[i], l)
            a = bb.frozen_apply(W, l, masks, H[i][None, :])[0]
            b = bb.forward(W, H[i][None, :], l)[0]
            assert np.allclose(a, b, rtol=1e-12, atol=1e-12)
        J = bb.frozen_matrix(W, l, bb.gate_path(W, H[0], l))
        assert np.allclose(J @ H[0], bb.forward(W, H[:1], l)[0], rtol=1e-10, atol=1e-10)


def test_residual_decomposition():
    """g(h) - J(c) h = sum_j J_{j->L}(c) r_j, r_j = (D_j(h) - D_j(c)) W_j h_{j-1} (Lemma 4.3)."""
    W = bb.make_weights(2, 12, 10)
    rng = np.random.default_rng(1)
    l = 3
    X = rng.standard_normal((2, 12))
    H = bb.forward(W, X, 0, l)
    h, c = H[0], H[1]
    mc = bb.gate_path(W, c, l)
    lhs = bb.forward(W, h[None, :], l)[0] - bb.frozen_apply(W, l, mc, h[None, :])[0]
    rhs = np.zeros(12)
    hj = h.copy()
    for j in range(l, len(W)):
        z = W[j] @ hj
        r = (z > 0).astype(float) * z - mc[j - l] * z
        # propagate r with c's gates from layer j+1 on
        v = r[None, :]
        for jj in range(j + 1, len(W)):
            v = (v @ W[jj].T) * mc[jj - l]
        rhs += v[0]
        hj = np.maximum(z, 0.0)
    assert np.allclose(lhs, rhs, rtol=1e-10, atol=1e-10)


def test_one_layer_law():
    """E_W |relu(W h) - D(c) W h|^2 = (2|h|^2/pi)(phi - sin phi cos phi); radial 2|h|^2(1 - kappa(cos phi))."""
    n = 32
    rng = np.random.default_rng(3)
    h = rng.standard_normal(n)
    u = rng.standard_normal(n)
    u -= (u @ h) / (h @ h) * h
    phi = 0.4
    c = math.cos(phi) * h / np.linalg.norm(h) + math.sin(phi) * u / np.linalg.norm(u)
    c *= np.linalg.norm(h)
    T = 40000
    eF, eR = np.zeros(T), np.zeros(T)
    for t in range(T):
        Wm = rng.standard_normal((n, n)) * math.sqrt(2.0 / n)
        z, zc = Wm @ h, Wm @ c
        a = np.maximum(z, 0.0)
        eF[t] = np.sum((a - (zc > 0) * z) ** 2)
        eR[t] = np.sum((a - np.maximum(zc, 0.0)) ** 2)
    h2 = h @ h
    predF = (2 * h2 / math.pi) * (phi - math.sin(phi) * math.cos(phi))
    predR = 2 * h2 * (1 - meanfield.kappa(math.cos(phi)))
    for est, pred in [(eF, predF), (eR, predR)]:
        se = est.std() / math.sqrt(T)
        assert abs(est.mean() - pred) < 4 * se, (est.mean(), pred, se)


def test_meanfield_one_layer_matches_formula():
    for phi in [0.01, 0.1, 0.5]:
        fr, ra = meanfield.residuals(phi, 1)
        assert abs(fr - (2 / math.pi) * (phi - math.sin(phi) * math.cos(phi))) < 1e-10
        assert abs(ra - 2 * (1 - meanfield.kappa(math.cos(phi)))) < 1e-10


def test_chain3_large_n_matches_meanfield():
    rng = np.random.default_rng(5)
    for Lp in [1, 8]:
        r = chain3.run(2048, Lp, 0.1, 600, rng)
        fr, ra = meanfield.residuals(0.1, Lp)
        assert abs(r['frozen'].mean() / fr - 1) < 0.12, (r['frozen'].mean(), fr)
        assert abs(r['radial'].mean() / ra - 1) < 0.12, (r['radial'].mean(), ra)


def test_chain3_against_nets():
    """Annealed chain mean equals the net average over fresh futures (n = 24, L' = 4, phi = 0.3)."""
    n, Lp, phi = 24, 4, 0.3
    rng = np.random.default_rng(7)
    ch = chain3.run(n, Lp, phi, 20000, rng)
    vals = []
    for s in range(3000):
        Wf = [rng.standard_normal((n, n)) * math.sqrt(2.0 / n) for _ in range(Lp)]
        h = np.abs(rng.standard_normal(n))
        u = rng.standard_normal(n)
        u -= (u @ h) / (h @ h) * h
        c = (math.cos(phi) * h / np.linalg.norm(h) + math.sin(phi) * u / np.linalg.norm(u)) * np.linalg.norm(h)
        masks = bb.gate_path(Wf, c, 0)
        g = bb.forward(Wf, h[None, :], 0)[0]
        f = bb.frozen_apply(Wf, 0, masks, h[None, :])[0]
        if g @ g > 0:
            vals.append(np.sum((g - f) ** 2) / (g @ g))
    vals = np.array(vals)
    # medians are robust to the heavy tail; compare medians within 15%
    assert abs(np.median(vals) / np.median(ch['frozen']) - 1) < 0.15, (np.median(vals), np.median(ch['frozen']))


def test_two_level_unbiased():
    """Telescoping: E G + E (A - G) = E A on the same samples (exact identity)."""
    W = bb.make_weights(3, 16, 16)
    rng = np.random.default_rng(9)
    U = bb.sphere(rng, 500, 16)
    H = bb.forward(W, U, 0, 6)
    A = bb.forward(W, H, 6)
    C = H[:3]
    masks = [bb.gate_path(W, C[k], 6) for k in range(3)]
    assign = np.argmax(bb.sphere(rng, 500, 3), axis=1)
    G = np.zeros_like(A)
    for k in range(3):
        sel = assign == k
        G[sel] = bb.frozen_apply(W, 6, masks[k], H[sel])
    assert np.allclose(G.mean(axis=0) + (A - G).mean(axis=0), A.mean(axis=0))
    # cell-sum form of the frozen level-1 mean
    cs = np.zeros(16)
    for k in range(3):
        sel = assign == k
        cs += bb.frozen_matrix(W, 6, masks[k]) @ H[sel].sum(axis=0)
    assert np.allclose(cs / 500, G.mean(axis=0), rtol=1e-9, atol=1e-12)


if __name__ == '__main__':
    for name, f in list(globals().items()):
        if name.startswith('test_') and callable(f):
            f()
            print('PASS', name, flush=True)
