"""Reverse water-filling and the spectra it is applied to (numpy float64).

rwf_rate(lam, D): Gaussian rate-distortion R(D) = sum_k max(0, (1/2) log2(lam_k / theta)), sum_k min(lam_k, theta) = D.
Spectra (FORMAL.md section 1.4, QUESTIONS.md A5):
  out_cov     eig Cov(a): the layer-free prediction for unrestricted encoders; attained in output space by the linear
              analog scheme (channel codes), an upper bound on the output's information rate-distortion function.
  lin_true    eig of K_1 = Cov(a, h) Sigma^+ Cov(h, a): the best linear predictor of a from h_l (true law), split-sample
              cross estimate (unbiased for K_1 up to the O(n/P) bias of Sigma^+).
  as_true     eig of E[Sigma^{1/2} J^T J Sigma^{1/2}], J the Jacobian of g_l at cloud points (true law), random
              cotangents: the high-resolution price of describing h_l with small errors (local encoders).
"""
import math

import numpy as np
import torch


def rwf_theta(lam, D):
    lam = np.sort(np.maximum(np.asarray(lam, float), 0.0))[::-1]
    if D >= lam.sum():
        return np.inf
    lo, hi = 0.0, lam[0]
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if np.minimum(lam, mid).sum() > D:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def rwf_rate(lam, D):
    lam = np.maximum(np.asarray(lam, float), 0.0)
    th = rwf_theta(lam, D)
    if not np.isfinite(th):
        return 0.0
    k = lam > th
    return float(0.5 * np.log2(lam[k] / th).sum())


def rwf_curve(lam, V, eps_list):
    return {float(e): rwf_rate(lam, e * V) for e in eps_list}


@torch.no_grad()
def sample_layers(net, layers, P, seed, chunk=8192):
    """float64 samples of h_l for each l in layers and the output a."""
    rng = np.random.default_rng(seed)
    H = {l: [] for l in layers}
    A = []
    for c0 in range(0, P, chunk):
        p = min(chunk, P - c0)
        h = rng.standard_normal((p, net.n))
        for k in range(net.L):
            if k in H:
                H[k].append(h.copy())
            h = np.maximum(h @ net.WT64[k], 0.0)
        A.append(h)
    return {l: np.concatenate(v) for l, v in H.items()}, np.concatenate(A)


def whiten(H, floor=1e-10):
    m = H.mean(0)
    S = np.cov(H, rowvar=False)
    w, U = np.linalg.eigh(S)
    w = np.maximum(w, 0.0)
    keep = w > floor * w.max()
    S12 = (U[:, keep] * np.sqrt(w[keep])) @ U[:, keep].T
    Sm12 = (U[:, keep] / np.sqrt(w[keep])) @ U[:, keep].T
    return m, S, S12, Sm12


def lin_spectrum(H, A):
    """Eigenvalues of K_1 = Cov(a, h) Sigma^+ Cov(h, a) by a split-sample cross estimate."""
    m, S, S12, Sm12 = whiten(H)
    Z = (H - m) @ Sm12
    Ac = A - A.mean(0)
    P = H.shape[0]
    h = P // 2
    B1 = Ac[:h].T @ Z[:h] / h            # n_out x n (regression in whitened coords)
    B2 = Ac[h:].T @ Z[h:] / (P - h)
    K = 0.5 * (B1 @ B2.T + B2 @ B1.T)
    ev = np.linalg.eigvalsh(K)[::-1]
    return ev


def as_spectrum(net, l, H, q=4, seed=0, chunk=2048):
    """Eigenvalues of E[Sigma^{1/2} J^T J Sigma^{1/2}] (true law) via VJPs with q Gaussian cotangents per sample."""
    m, S, S12, Sm12 = whiten(H)
    n = net.n
    C = np.zeros((n, n))
    g = torch.Generator().manual_seed(seed)
    cnt = 0
    WT = [torch.tensor(w, dtype=torch.float64) for w in net.WT64]
    for c0 in range(0, H.shape[0], chunk):
        hb = torch.tensor(H[c0:c0 + chunk], dtype=torch.float64)
        masks = []
        x = hb
        for k in range(l, net.L):
            z = x @ WT[k]
            masks.append(z > 0)
            x = torch.relu(z)
        for _ in range(q):
            u = torch.randn(x.shape, generator=g, dtype=torch.float64)
            for k in reversed(range(l, net.L)):
                u = (u * masks[k - l]) @ WT[k].T
            v = u.numpy() @ S12
            C += v.T @ v
            cnt += v.shape[0]
    C /= cnt
    return np.linalg.eigvalsh(C)[::-1], float(np.trace(C))
