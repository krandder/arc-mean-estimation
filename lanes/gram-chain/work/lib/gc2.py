"""Exact replica Gram chain of Model S, version 2 (gram-chain lane, 1 Nov 2026).

Model S: h_l = relu(W_l h_{l-1}) + sigma xi_l, W_l iid N(0, 2/n), xi_l iid N(0, I_n). R replicas share every W_l.
Given the past, the rows w_i of W_l are iid N(0, (2/n) I) and independent of it, so the pre-activation vectors across
replicas z_i = (w_i . h^(a))_a are iid over units i with law N(0, 2 G), G_ab = h^(a).h^(b)/n. The new Gram matrix is
  G' = (1/n) sum_i v_i v_i^T,   v_i = relu(z_i) + sigma xi_i,
with xi_i iid over i. Hence G is an exact Markov chain (numerics lane P-G1).

Extensions in v2 (all exact by the same argument: the next layer sees the past only through the joint Gram matrix of
every vector the rows of W_l act on):
  - noise correlation matrices S (any PSD R_s x R_s), per-chain equivalence labels, and per-coordinate Bernoulli
    sharing between replica pairs;
  - tangent replicas: t' = D(z_base) W t (no noise), v_i[t] = 1[z_i[base] > 0] z_i[t];
  - Gram surgery (perturbation of relative size eps orthogonal to the span of given replicas, radius rescaling);
  - sigma = 0 (input regime), exact Wishart initial Gram matrices for independent Gaussian inputs;
  - the noiseless output layer a = relu(W_L h) as one more step, with closed-form conditional expectations.
Index conventions: G has shape (P, R, R) for P independent chains. Replicas 0..Rs-1 are states; replicas Rs..R-1 are
tangent vectors attached (by `tan_base`) to a state replica.
"""
import math
import numpy as np

PI = math.pi
C_K = 2.0 * math.sqrt(2.0) / (3.0 * PI)  # 1 - kappa(1 - d) = d - C_K d^{3/2} - d^{5/2}/(15 sqrt2 pi) + ...


def kappa(c):
    """E[relu(u) relu(v)] / (E relu(u)^2 E relu(v)^2)^{1/2}... normalised so that E[relu(z_a) relu(z_b)] =
    sqrt(G_aa G_bb) kappa(rho) for z ~ N(0, 2G): kappa(rho) = (sqrt(1 - rho^2) + (pi - arccos rho) rho)/pi."""
    c = np.clip(c, -1.0, 1.0)
    return (np.sqrt(np.maximum(1.0 - c * c, 0.0)) + (PI - np.arccos(c)) * c) / PI


def f_kernel(d):
    """1 - kappa(1 - d): the per-layer finite-angle term."""
    return 1.0 - kappa(1.0 - d)


def sym_sqrt(M):
    """Batched symmetric PSD square root (P, R, R); exact for rank-deficient M."""
    w, V = np.linalg.eigh(M)
    return np.einsum('pab,pb,pcb->pac', V, np.sqrt(np.maximum(w, 0.0)), V)


def _labels(share):
    R = share.shape[0]
    lab = -np.ones(R, int)
    c = 0
    for i in range(R):
        if lab[i] < 0:
            for j in range(R):
                if share[i, j]:
                    lab[j] = c
            c += 1
    return lab


def preacts(G, n, rng):
    """z (P, n, R): rows iid N(0, 2 G) per chain."""
    P, R, _ = G.shape
    if R == 1:
        return np.sqrt(2.0 * np.maximum(G[:, 0, 0], 0.0))[:, None, None] * rng.standard_normal((P, n, 1))
    if R == 2:
        g11, g22, g12 = G[:, 0, 0], G[:, 1, 1], G[:, 0, 1]
        rho = np.clip(g12 / np.sqrt(np.maximum(g11 * g22, 1e-300)), -1.0, 1.0)
        N = rng.standard_normal((P, n, 2))
        z1 = np.sqrt(2 * g11)[:, None] * N[:, :, 0]
        z2 = np.sqrt(2 * g22)[:, None] * (rho[:, None] * N[:, :, 0] + np.sqrt(1 - rho * rho)[:, None] * N[:, :, 1])
        return np.stack([z1, z2], 2)
    return np.einsum('pab,pib->pia', sym_sqrt(2.0 * G), rng.standard_normal((P, n, R)))


def noise(P, n, Rs, rng, S=None, labels=None, coord=None):
    """Noise (P, n, Rs) for the Rs state replicas.
    S: (Rs, Rs) PSD correlation matrix (shared by all chains); labels: (P, Rs) ints (equal label = same noise vector);
    coord: list of (a, b, t): replica b's noise coordinate i equals replica a's with probability t, independently over
    units (applied after the base draw; b must not be listed as a source later). Default: independent."""
    if S is not None:
        L = sym_sqrt(np.asarray(S, float)[None])[0]
        x = rng.standard_normal((P, n, Rs)) @ L.T
    elif labels is not None:
        labels = np.asarray(labels)
        if labels.ndim == 1:
            x = rng.standard_normal((P, n, labels.max() + 1))[:, :, labels]
        else:
            x = np.take_along_axis(rng.standard_normal((P, n, Rs)),
                                   np.broadcast_to(labels[:, None, :], (P, n, Rs)), axis=2)
    else:
        x = rng.standard_normal((P, n, Rs))
    if coord is not None:
        for a, b, t in coord:
            m = rng.random((P, n)) < t
            x[:, :, b] = np.where(m, x[:, :, a], x[:, :, b])
    return x


def step(G, n, rng, sigma=1.0, Rs=None, tan_base=None, S=None, labels=None, coord=None, out=False):
    """One exact layer for P chains. G: (P, R, R). Rs: number of state replicas (default R); replicas Rs.. are tangents
    with base state index tan_base[k]. out=True: the noiseless output layer a = relu(W h) (tangents: D W t)."""
    P, R, _ = G.shape
    Rs = R if Rs is None else Rs
    z = preacts(G, n, rng)
    v = np.empty_like(z)
    v[:, :, :Rs] = np.maximum(z[:, :, :Rs], 0.0)
    if R > Rs:
        for k, b in enumerate(tan_base):
            v[:, :, Rs + k] = (z[:, :, b] > 0) * z[:, :, Rs + k]
    if not out and sigma != 0.0:
        v[:, :, :Rs] += sigma * noise(P, n, Rs, rng, S=S, labels=labels, coord=coord)
    return np.einsum('pia,pib->pab', v, v) / n


def out_mean(G):
    """E[G_out | G] for the noiseless output layer (states only): sqrt(G_aa G_bb) kappa(rho_ab)."""
    d = np.sqrt(np.maximum(np.einsum('pii->pi', G), 0.0))
    dd = d[:, :, None] * d[:, None, :]
    rho = np.where(dd > 0, G / np.maximum(dd, 1e-300), 1.0)
    return dd * kappa(rho)


def init_identical(Q, R):
    """All R replicas equal to one state of radius Q (P,)."""
    return np.repeat(np.repeat(np.asarray(Q, float)[:, None, None], R, 1), R, 2)


def wishart_inputs(n, P, R, rng):
    """Gram of R independent N(0, I_n) inputs: (1/n) X^T X, exact."""
    X = rng.standard_normal((P, n, R))
    return np.einsum('pia,pib->pab', X, X) / n


def surgery_perturb(G, base, eps, n_new=1):
    """Append n_new replicas, each equal to replica `base` plus a perturbation of squared norm eps^2 |h_base|^2
    orthogonal to every existing replica and to each other (exactly representable: only the Gram matrix matters,
    valid while R + n_new <= n). Returns the enlarged Gram (P, R + n_new, R + n_new)."""
    P, R, _ = G.shape
    H = np.zeros((P, R + n_new, R + n_new))
    H[:, :R, :R] = G
    for k in range(n_new):
        j = R + k
        H[:, j, :R] = G[:, base, :]
        H[:, :R, j] = G[:, :, base]
        for k2 in range(n_new):
            j2 = R + k2
            H[:, j, j2] = G[:, base, base] * (1.0 + (eps * eps if j2 == j else 0.0))
    return H


def add_tangents(G, base, k, scale=1.0):
    """Append k tangent vectors at state `base`, orthonormal among themselves (norm^2/n = scale^2 |h_base|^2/n... here
    |t|^2/n = scale^2) and orthogonal to all states. Returns enlarged G and the tan_base list."""
    P, R, _ = G.shape
    H = np.zeros((P, R + k, R + k))
    H[:, :R, :R] = G
    for j in range(k):
        H[:, R + j, R + j] = scale * scale
    return H, [base] * k


def diffs(G, n, i=0, j=1, out_closed=True):
    """Pair functionals of the final hidden Gram (P, R, R) between replicas i, j (states)."""
    g11, g22, g12 = G[:, i, i], G[:, j, j], G[:, i, j]
    rho = np.clip(g12 / np.sqrt(np.maximum(g11 * g22, 1e-300)), -1.0, 1.0)
    res = dict(h=n * (g11 + g22 - 2 * g12), u=2 * (1 - rho), delta=1 - rho, logR=0.25 * (np.log(g11) - np.log(g22)) ** 2,
               g=n * np.arccos(rho) / PI, rho=rho, Q=0.5 * (g11 + g22), ell=0.5 * np.log(g11 / g22))
    if out_closed:  # E|a_i - a_j|^2 given G, a = relu(W h) with fresh W (exact conditional expectation)
        res['a'] = n * (g11 + g22 - 2 * np.sqrt(g11 * g22) * kappa(rho))
    return res


def sample_Q_stationary(n, P, rng, steps=None, init='invgamma'):
    """Stationary radius Q = |h|^2/n (sigma = 1) by running the exact scalar chain Q' = (S/n)(1 + 2 Q beta) from the
    large-n inverse-gamma law (Q/n = 2/(5 Z), Z ~ Exp(1)); default 20 n steps (the chain mixes in O(n) layers)."""
    steps = 20 * n if steps is None else steps
    Q = n * 2.0 / (5.0 * rng.exponential(size=P)) if init == 'invgamma' else np.full(P, 0.58 * n)
    for _ in range(steps):
        M = rng.binomial(n, 0.5, P)
        b = np.where(M == 0, 0.0, np.where(M == n, 1.0,
                                           rng.beta(np.maximum(M, 1) / 2.0, np.maximum(n - M, 1) / 2.0)))
        Q = rng.chisquare(n, P) / n * (1.0 + 2.0 * Q * b)
    return Q


def mf_fixed_point(Q, c=0.0):
    """Mean-field angle fixed point: delta (Q + 1) = (1 - c) + Q (1 - kappa(1 - delta)), vectorised bisection."""
    Q = np.atleast_1d(np.asarray(Q, float))
    lo = np.full(Q.shape, 1e-14)
    hi = np.full(Q.shape, 2.0)
    for _ in range(80):
        d = 0.5 * (lo + hi)
        g = d * (Q + 1) - (1 - c) - Q * f_kernel(d)
        hi = np.where(g > 0, d, hi)
        lo = np.where(g > 0, lo, d)
    return 0.5 * (lo + hi)


def mf_delta_star_series(Q, c=0.0):
    """Two-term expansion of the mean-field fixed point."""
    eps = ((1 - c) / (C_K * np.asarray(Q, float))) ** (2.0 / 3.0)
    return eps * (1 - (2.0 / (3.0 * (1 - c)) + 1.0 / 30.0) * eps)
