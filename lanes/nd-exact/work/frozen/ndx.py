"""nd-exact core: narrow-deep plain ReLU nets (width 8, depth 256, sigma = 0), forward passes, activation patterns.

Nets are exactly work/narrow-deep/lib/nd.make_weights('plain', seed, n, L) (verified in tests/test_ndx.py), rebuilt here
in numpy: W_l iid N(0, 2/n), no biases, h_l = relu(W_l h_{l-1}), output a = h_L (the last layer is also a ReLU).
Input x ~ N(0, I_n). Estimand E[a] in R^n, scored by nMSE = |est - truth|^2 / tr Var(a).
"""
import math

import numpy as np

LMAX = 256
P1 = np.uint64(0x9E3779B97F4A7C15)
P2 = np.uint64(0xC2B2AE3D27D4EB4F)


def make_weights(seed, n=8, L=256):
    """Identical to nd.make_weights('plain', seed, n, L): list of L arrays (n, n)."""
    rs = np.random.RandomState((2_000_003 + 7919 * seed + 104729 * n + 0) % (2 ** 32))
    lm = max(LMAX, L)
    W = [rs.standard_normal((n, n)) * math.sqrt(2.0 / n) for _ in range(lm)][:L]
    return W


def fwd(Ws, X, a=0, b=None):
    """Apply layers a+1..b (0-indexed weights a..b-1) to rows of X."""
    b = len(Ws) if b is None else b
    h = X
    for k in range(a, b):
        h = np.maximum(h @ Ws[k].T, 0.0)
    return h


def fwd_patterns(Ws, X, a=0, b=None):
    """Forward with packed activation bits per layer: returns h_b and pat (N, b-a) uint8 (bit j = unit j active)."""
    b = len(Ws) if b is None else b
    h = X
    pat = np.empty((X.shape[0], b - a), dtype=np.uint8)
    for i, k in enumerate(range(a, b)):
        z = h @ Ws[k].T
        act = z > 0
        pat[:, i] = np.packbits(act, axis=1, bitorder='little')[:, 0]
        h = np.where(act, z, 0.0)
    return h, pat


def hash2(pat):
    """Two independent 64-bit polynomial hashes of each row of a uint8 pattern array (N, m). Returns (N, 2) uint64."""
    N, m = pat.shape
    h1 = np.zeros(N, dtype=np.uint64)
    h2 = np.zeros(N, dtype=np.uint64)
    with np.errstate(over='ignore'):
        for i in range(m):
            b = pat[:, i].astype(np.uint64) + np.uint64(1)
            h1 = h1 * P1 + b
            h2 = h2 * P2 + (b ^ np.uint64(0x5A))
    return np.stack([h1, h2], axis=1)


def void_keys(arr):
    """Row-wise exact keys for np.unique."""
    a = np.ascontiguousarray(arr)
    return a.view(np.dtype((np.void, a.dtype.itemsize * a.shape[1]))).ravel()


def chi_mean(n):
    """E|x| for x ~ N(0, I_n)."""
    return math.sqrt(2.0) * math.exp(math.lgamma((n + 1) / 2) - math.lgamma(n / 2))


def nmse(est, truth, trV):
    d = np.asarray(est, dtype=float) - np.asarray(truth, dtype=float)
    return float(np.sum(d * d) / trV)


DEV_SEEDS = [103, 110, 111, 129, 133, 137, 141, 150, 153, 154, 160, 163]
EVAL_SEEDS = [203, 216, 217, 220, 221, 223]
SPARE_SEEDS = [224, 230, 235, 236, 241, 246, 253, 254, 259]
