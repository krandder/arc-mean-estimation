"""Bits-bounds lane: nets, frozen-gate (linearised) futures, residuals, cloud geometry.

Net: width n, depth L, W_l iid N(0, 2/n) (n x n), no bias, x ~ N(0, I_n); h_0 = x, h_l = relu(W_l h_{l-1}),
output a = h_L. Row convention: a batch of states is an (N, n) array H; one layer maps H -> relu(H @ W_l.T).

Future map from layer l: g_l(h) = layers l+1..L applied to h (positively 1-homogeneous, piecewise linear).
Frozen-gate future at a reference state c (layer l): J_l(c) v = D_L W_L ... D_{l+1} W_{l+1} v, where D_j is the gate
pattern of c's own trajectory at layer j (D_j = diag(1{W_j c_{j-1} > 0})). Euler: g_l(c) = J_l(c) c, and
g_l(h) = J_l(h) h for every h. Hence the linearisation residual of h at reference c is
    R(h; c) = g_l(h) - [g_l(c) + J_l(c)(h - c)] = g_l(h) - J_l(c) h = (J_l(h) - J_l(c)) h,
caused only by the future gates on which h's and c's trajectories disagree.

Cost unit: one n x n matrix-vector product ("mv", 2 n^2 FLOPs). float64 numpy. Single-threaded BLAS is expected
(set OMP_NUM_THREADS / OPENBLAS_NUM_THREADS before import in run scripts).
"""
import math
import numpy as np
from scipy.special import gammaln

SEED_BASE = 20261101


def make_weights(seed, n, L):
    """List of L weight matrices W_l (n x n), iid N(0, 2/n); seeded by (SEED_BASE, seed, n, L)."""
    rng = np.random.default_rng([SEED_BASE, int(seed), int(n), int(L)])
    return [rng.standard_normal((n, n)) * math.sqrt(2.0 / n) for _ in range(L)]


def mean_radius(n):
    """E|x| for x ~ N(0, I_n)."""
    return math.exp(0.5 * math.log(2.0) + gammaln((n + 1) / 2.0) - gammaln(n / 2.0))


def sphere(rng, N, n):
    G = rng.standard_normal((N, n))
    return G / np.linalg.norm(G, axis=1, keepdims=True)


def forward(W, H, l0=0, l1=None):
    """Propagate states H (N, n) from layer l0 to layer l1 (default L): applies W[l0], ..., W[l1-1]."""
    if l1 is None:
        l1 = len(W)
    for j in range(l0, l1):
        H = np.maximum(H @ W[j].T, 0.0)
    return H


def forward_keep(W, H, keep):
    """Forward from layer 0; return dict {l: H_l} for l in keep (0 <= l <= L)."""
    keep = set(int(k) for k in keep)
    out = {}
    if 0 in keep:
        out[0] = H.copy()
    for j in range(len(W)):
        H = np.maximum(H @ W[j].T, 0.0)
        if j + 1 in keep:
            out[j + 1] = H.copy()
    return out


def gate_path(W, c, l):
    """Gate masks (list of boolean (n,) arrays) of the reference state c (n,) at layers l+1..L."""
    masks = []
    h = np.asarray(c, dtype=float)
    for j in range(l, len(W)):
        z = W[j] @ h
        m = z > 0
        masks.append(m)
        h = np.where(m, z, 0.0)
    return masks


def frozen_apply(W, l, masks, V):
    """J_l(c) applied to rows of V (N, n): propagate with the frozen gate masks of c (from gate_path)."""
    for j, m in zip(range(l, len(W)), masks):
        V = (V @ W[j].T) * m
    return V


def frozen_matrix(W, l, masks):
    """The n x n matrix J_l(c) (product of masked layers), cost about L' n^3."""
    n = W[0].shape[0]
    J = np.eye(n)
    for j, m in zip(range(l, len(W)), masks):
        J = (W[j] * m[:, None]) @ J
    return J


def angles_to(H, c):
    """Angles (radians) between rows of H and vector c."""
    hn = np.linalg.norm(H, axis=1)
    cn = np.linalg.norm(c)
    cos = (H @ c) / np.maximum(hn * cn, 1e-300)
    return np.arccos(np.clip(cos, -1.0, 1.0))


def kmeans_dirs(U, M, rng, iters=25):
    """Spherical k-means on unit rows U (N, n): returns centres (M, n) (unit) and assignment (N,)."""
    N = U.shape[0]
    if M >= N:
        return U.copy(), np.arange(N)
    C = U[rng.choice(N, M, replace=False)].copy()
    assign = np.zeros(N, dtype=int)
    for _ in range(iters):
        S = U @ C.T
        new = np.argmax(S, axis=1)
        if _ > 0 and np.array_equal(new, assign):
            break
        assign = new
        for k in range(M):
            sel = assign == k
            if np.any(sel):
                v = U[sel].sum(axis=0)
                nv = np.linalg.norm(v)
                if nv > 0:
                    C[k] = v / nv
            else:
                C[k] = U[rng.integers(N)]
    # recompute the assignment for the final centres (fixed after the registered runs; review finding 11)
    assign = np.argmax(U @ C.T, axis=1)
    return C, assign


def cloud_angular_spectrum(H):
    """Eigenvalues (descending) of the covariance of the unit directions of the rows of H (angular cloud)."""
    U = H / np.maximum(np.linalg.norm(H, axis=1, keepdims=True), 1e-300)
    U = U - U.mean(axis=0, keepdims=True)
    ev = np.linalg.eigvalsh(U.T @ U / U.shape[0])[::-1]
    return np.maximum(ev, 0.0)


def participation_ratio(ev):
    s = ev.sum()
    return float(s * s / max((ev * ev).sum(), 1e-300))
