"""Tests of lib/gc2.py against explicit networks with fresh random weights (annealed comparison).
Each test runs T independent trials of an explicit width-n net (fresh W_l each layer) and the same number of Gram-chain
runs from the same initial Gram matrix, and compares scalar functionals by two-sample KS tests (p > 1e-3) and mean
z-scores (|z| < 4). Run: python tests/test_gc2.py  (prints one line per check, exits 1 on any failure)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))
import numpy as np
from scipy.stats import ks_2samp
import gc2

FAIL = []


def check(name, x_net, x_chain):
    x_net, x_chain = np.asarray(x_net, float), np.asarray(x_chain, float)
    p = ks_2samp(x_net, x_chain).pvalue
    z = (x_net.mean() - x_chain.mean()) / math.sqrt(x_net.var() / x_net.size + x_chain.var() / x_chain.size + 1e-300)
    ok = p > 1e-3 and abs(z) < 4
    print('%-58s KS p=%.3g  z=%+.2f  mean net %.5g chain %.5g  %s' % (name, p, z, x_net.mean(), x_chain.mean(),
                                                                      'ok' if ok else 'FAIL'), flush=True)
    if not ok:
        FAIL.append(name)


def net_states(H0, Ws, noise_fn, sigma=1.0, out=False):
    """H0: (T, n, Rs) states; Ws: list of (T, n, n) weights; noise_fn(l) -> (T, n, Rs)."""
    H = H0
    for l, W in enumerate(Ws):
        Z = np.einsum('tij,tja->tia', W, H)
        H = np.maximum(Z, 0.0)
        if not (out and l == len(Ws) - 1) and sigma != 0.0:
            H = H + sigma * noise_fn(l)
    return H


def gram(H, n):
    return np.einsum('tia,tib->tab', H, H) / n


def fresh_W(T, n, rng):
    return rng.standard_normal((T, n, n)) * math.sqrt(2.0 / n)


def states_with_gram(G0, n, rng):
    """Vectors (n x R) with Gram exactly G0 (R x R): orthonormal frame times sqrt(n G0)."""
    R = G0.shape[0]
    Qm, _ = np.linalg.qr(rng.standard_normal((n, R)))
    w, V = np.linalg.eigh(n * G0)
    return Qm @ (V * np.sqrt(np.maximum(w, 0))) @ V.T


def test_corr_noise(rng, n=16, T=4000, L=10, c=0.5):
    G0 = np.array([[0.6 * n, 0.6 * n], [0.6 * n, 0.6 * n]])
    S = np.array([[1, c], [c, 1]])
    Ls = np.linalg.cholesky(S)
    H = np.repeat(states_with_gram(G0, n, rng)[None], T, 0)
    Ws = [fresh_W(T, n, rng) for _ in range(L)]
    Hn = net_states(H, Ws, lambda l: rng.standard_normal((T, n, 2)) @ Ls.T)
    Gn = gram(Hn, n)
    G = np.repeat(G0[None], T, 0)
    for _ in range(L):
        G = gc2.step(G, n, rng, S=S)
    dn, dc = gc2.diffs(Gn, n), gc2.diffs(G, n)
    check('R=2 noise corr 0.5: delta', dn['delta'], dc['delta'])
    check('R=2 noise corr 0.5: Q', dn['Q'], dc['Q'])
    check('R=2 noise corr 0.5: ell', dn['ell'], dc['ell'])


def test_labels(rng, n=16, T=4000, L=10, j=4):
    G0 = 0.6 * n * np.ones((3, 3))
    H = np.repeat(states_with_gram(G0, n, rng)[None], T, 0)
    Ws = [fresh_W(T, n, rng) for _ in range(L)]
    labs = [np.array([0, 0, 1]) if l != j else np.array([0, 2, 1]) for l in range(L)]

    def nf(l):
        x = rng.standard_normal((T, n, 3))
        return x[:, :, labs[l]]
    Gn = gram(net_states(H, Ws, nf), n)
    G = np.repeat(G0[None], T, 0)
    for l in range(L):
        G = gc2.step(G, n, rng, labels=labs[l])
    for (a, b) in [(0, 1), (0, 2)]:
        check('R=3 labels (0,1 share except layer %d): delta_%d%d' % (j, a, b), gc2.diffs(Gn, n, a, b)['delta'],
              gc2.diffs(G, n, a, b)['delta'])


def test_coord(rng, n=16, T=4000, L=10, t=0.5):
    G0 = 0.6 * n * np.ones((2, 2))
    H = np.repeat(states_with_gram(G0, n, rng)[None], T, 0)
    Ws = [fresh_W(T, n, rng) for _ in range(L)]

    def nf(l):
        x = rng.standard_normal((T, n, 2))
        m = rng.random((T, n)) < t
        x[:, :, 1] = np.where(m, x[:, :, 0], x[:, :, 1])
        return x
    Gn = gram(net_states(H, Ws, nf), n)
    G = np.repeat(G0[None], T, 0)
    for _ in range(L):
        G = gc2.step(G, n, rng, coord=[(0, 1, t)])
    check('R=2 coordinate sharing t=0.5: delta', gc2.diffs(Gn, n)['delta'], gc2.diffs(G, n)['delta'])


def test_tangent(rng, n=16, T=4000, L=8):
    # one state + 2 tangents orthogonal to it and to each other, |t|^2/n = 1
    Q0 = 0.6 * n
    G0 = np.diag([Q0, 1.0, 1.0])
    H = np.repeat(states_with_gram(G0, n, rng)[None], T, 0)  # columns: h, t1, t2
    for l in range(L):
        W = fresh_W(T, n, rng)
        Z = np.einsum('tij,tja->tia', W, H)
        D = (Z[:, :, :1] > 0)
        Hs = np.maximum(Z[:, :, :1], 0) + rng.standard_normal((T, n, 1))
        H = np.concatenate([Hs, D * Z[:, :, 1:]], 2)
    Gn = gram(H, n)
    G = np.repeat(G0[None], T, 0)
    for _ in range(L):
        G = gc2.step(G, n, rng, Rs=1, tan_base=[0, 0])
    check('tangent: |J t1|^2/n (annealed mean must be 1)', Gn[:, 1, 1], G[:, 1, 1])
    check('tangent: (J t1 . J t2)/n', Gn[:, 1, 2], G[:, 1, 2])
    check('tangent: (J t1 . h)/n', Gn[:, 0, 1], G[:, 0, 1])
    z = (G[:, 1, 1].mean() - 1.0) / (G[:, 1, 1].std() / math.sqrt(T))
    print('%-58s z=%+.2f %s' % ('tangent: chain E|J t|^2/n = 1 exactly', z, 'ok' if abs(z) < 4 else 'FAIL'))
    if abs(z) >= 4:
        FAIL.append('tangent mean')


def test_surgery(rng, n=16, T=4000, L=8, eps=0.3):
    G0 = 0.6 * n * np.ones((1, 1))
    Gs = gc2.surgery_perturb(G0[None], 0, eps, n_new=2)[0]
    H = np.repeat(states_with_gram(Gs, n, rng)[None], T, 0)
    Ws = [fresh_W(T, n, rng) for _ in range(L)]
    Gn = gram(net_states(H, Ws, lambda l: rng.standard_normal((T, n, 1))[:, :, [0, 0, 0]]), n)
    G = np.repeat(Gs[None], T, 0)
    for _ in range(L):
        G = gc2.step(G, n, rng, labels=np.array([0, 0, 0]))
    check('surgery eps=0.3, shared noise: delta_01', gc2.diffs(Gn, n, 0, 1)['delta'], gc2.diffs(G, n, 0, 1)['delta'])
    x_n = n * (Gn[:, 1, 2] - Gn[:, 0, 1] - Gn[:, 0, 2] + Gn[:, 0, 0])
    x_c = n * (G[:, 1, 2] - G[:, 0, 1] - G[:, 0, 2] + G[:, 0, 0])
    check('surgery: (d1 . d2) of the two perturbations', x_n, x_c)


def test_inputs(rng, n=16, T=4000, L=8):
    X = rng.standard_normal((T, n, 3))
    Gn0 = gram(X, n)
    Ws = [fresh_W(T, n, rng) for _ in range(L)]
    Gn = gram(net_states(X, Ws, None, sigma=0.0), n)
    G = gc2.wishart_inputs(n, T, 3, rng)
    for _ in range(L):
        G = gc2.step(G, n, rng, sigma=0.0)
    check('inputs sigma=0: initial Wishart rho_01', gc2.diffs(Gn0, n)['rho'], gc2.diffs(gc2.wishart_inputs(n, T, 3, rng), n)['rho'])
    check('inputs sigma=0, L=8: delta_01', gc2.diffs(Gn, n, 0, 1)['delta'], gc2.diffs(G, n, 0, 1)['delta'])
    check('inputs sigma=0, L=8: sqrt Q_0 (exact zeros possible)', np.sqrt(Gn[:, 0, 0]), np.sqrt(G[:, 0, 0]))


def test_output(rng, n=16, T=20000):
    G0 = np.array([[10.0, 7.0], [7.0, 8.0]])
    G = np.repeat(G0[None], T, 0)
    Go = gc2.step(G, n, rng, out=True)
    m = gc2.out_mean(G0[None])[0]
    for (a, b) in [(0, 0), (0, 1), (1, 1)]:
        z = (Go[:, a, b].mean() - m[a, b]) / (Go[:, a, b].std() / math.sqrt(T))
        ok = abs(z) < 4
        print('%-58s z=%+.2f %s' % ('output layer closed form E[G_out[%d,%d]|G]' % (a, b), z, 'ok' if ok else 'FAIL'))
        if not ok:
            FAIL.append('out_mean')


def test_fixed_point():
    Q = np.array([100.0, 1000.0, 10000.0])
    d = gc2.mf_fixed_point(Q)
    s = gc2.mf_delta_star_series(Q)
    rel = np.abs(s / d - 1)
    ok = rel[1] < 3e-4 and rel[2] < 2e-5
    print('%-58s rel.err %s %s' % ('mean-field fixed point vs two-term series', np.array2string(rel, precision=2), 'ok' if ok else 'FAIL'))
    if not ok:
        FAIL.append('fixed point')


if __name__ == '__main__':
    rng = np.random.default_rng(20261101)
    test_corr_noise(rng)
    test_labels(rng)
    test_coord(rng)
    test_tangent(rng)
    test_surgery(rng)
    test_inputs(rng)
    test_output(rng)
    test_fixed_point()
    print('FAILED: %s' % FAIL if FAIL else 'ALL PASS')
    sys.exit(1 if FAIL else 0)
