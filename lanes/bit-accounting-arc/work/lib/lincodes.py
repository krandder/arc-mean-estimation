"""Linear transform codes at layer l (no training): the baseline every learned code must beat, and the learned codes'
initialisation.

A linear code at layer l: whitened state z = Sigma^{-1/2} (h_l - m), components u_k = q_k . z along an orthonormal basis
q_1, q_2, ... ordered by importance lambda_k; the decoder reconstructs z_hat = sum_k u_hat_k q_k, h_hat = m + Sigma^{1/2}
z_hat, and the fixed future is applied: a_hat = g_l(h_hat). Bases: 'as' (active subspace E[S J^T J S], S = Sigma^{1/2}),
'lin' (degree-1 relevance K_1 in whitened coordinates, B^T B with B = Cov(a, z)), 'out' (output-space PCA, layer L).
  channel (analog): capacities by reverse water-filling of lambda at total C, SNR_k = 2^{2 C_k} - 1, linear MMSE decoding;
  binary: integer bits b_k by greedy allocation with the Lloyd-Max distortion table of N(0, 1), Lloyd-Max quantisers.
"""
import math

import numpy as np
import torch



# ----------------------------------------------------------------------------------------------------------------------
# Lloyd-Max quantisers of N(0, 1)
# ----------------------------------------------------------------------------------------------------------------------

def _lloyd_max(b, grid=200001, iters=300):
    from scipy.stats import norm
    L = 2 ** b
    x = np.linspace(-8, 8, grid)
    w = norm.pdf(x)
    w /= w.sum()
    lev = norm.ppf((np.arange(L) + 0.5) / L)
    for _ in range(iters):
        th = 0.5 * (lev[1:] + lev[:-1])
        idx = np.searchsorted(th, x)
        num = np.bincount(idx, weights=w * x, minlength=L)
        den = np.bincount(idx, weights=w, minlength=L)
        lev = num / np.maximum(den, 1e-300)
    th = 0.5 * (lev[1:] + lev[:-1])
    idx = np.searchsorted(th, x)
    D = float(np.sum(w * (x - lev[idx]) ** 2))
    return lev, th, D


_LM = {}


def lloyd_max(b):
    if b not in _LM:
        if b <= 12:
            _LM[b] = _lloyd_max(b, grid=400001 if b > 9 else 200001)
        else:   # fine uniform quantiser (Panter-Dite regime)
            L = 2 ** b
            step = 2 * 6.0 / L
            lev = -6.0 + step * (np.arange(L) + 0.5)
            th = 0.5 * (lev[1:] + lev[:-1])
            _LM[b] = (lev, th, (math.sqrt(3) * math.pi / 2) * 4.0 ** (-b))
    return _LM[b]


def lm_dist(b):
    return 1.0 if b == 0 else lloyd_max(b)[2]


def quantise(u, b):
    lev, th, _ = lloyd_max(b)
    return lev[np.searchsorted(th, u)]


def greedy_bits(lam, B, bmax=12):
    """Integer bit allocation maximising the reduction of sum_k lam_k d(b_k) one bit at a time."""
    lam = np.asarray(lam, float)
    bits = np.zeros(len(lam), int)
    gain = lam * (1.0 - lm_dist(1))
    for _ in range(int(B)):
        k = int(np.argmax(gain))
        if gain[k] <= 0:
            break
        bits[k] += 1
        if bits[k] >= bmax:
            gain[k] = -1.0
        else:
            gain[k] = lam[k] * (lm_dist(bits[k]) - lm_dist(bits[k] + 1))
    return bits


# ----------------------------------------------------------------------------------------------------------------------
# Bases
# ----------------------------------------------------------------------------------------------------------------------

def frame(H, floor=1e-10):
    m = H.mean(0)
    S = np.cov(H, rowvar=False)
    w, U = np.linalg.eigh(S)
    w = np.maximum(w, 0.0)
    keep = w > floor * w.max()
    S12 = (U[:, keep] * np.sqrt(w[keep])) @ U[:, keep].T
    Sm12 = (U[:, keep] / np.sqrt(w[keep])) @ U[:, keep].T
    return dict(m=m, S12=S12, Sm12=Sm12)


def basis_as(net, l, H, fr, q=4, seed=0, chunk=2048):
    n = net.n
    C = np.zeros((n, n))
    g = torch.Generator().manual_seed(seed)
    WT = [torch.tensor(w, dtype=torch.float64) for w in net.WT64]
    cnt = 0
    for c0 in range(0, H.shape[0], chunk):
        x = torch.tensor(H[c0:c0 + chunk], dtype=torch.float64)
        masks = []
        for k in range(l, net.L):
            z = x @ WT[k]
            masks.append(z > 0)
            x = torch.relu(z)
        for _ in range(q):
            u = torch.randn(x.shape, generator=g, dtype=torch.float64)
            for k in reversed(range(l, net.L)):
                u = (u * masks[k - l]) @ WT[k].T
            v = u.numpy() @ fr['S12']
            C += v.T @ v
            cnt += v.shape[0]
    C /= cnt
    w, U = np.linalg.eigh(C)
    return np.maximum(w[::-1], 0.0), U[:, ::-1].copy()


def basis_lin(H, A, fr):
    Z = (H - fr['m']) @ fr['Sm12']
    Ac = A - A.mean(0)
    P = H.shape[0]
    h = P // 2
    B1 = Ac[:h].T @ Z[:h] / h
    B2 = Ac[h:].T @ Z[h:] / (P - h)
    K = 0.5 * (B1.T @ B2 + B2.T @ B1)     # n x n in whitened state coordinates
    w, U = np.linalg.eigh(K)
    return np.maximum(w[::-1], 0.0), U[:, ::-1].copy()


# ----------------------------------------------------------------------------------------------------------------------
# Evaluation of linear codes
# ----------------------------------------------------------------------------------------------------------------------

def eval_linear(net, l, fr, lam, Q, H, A, V, rates, kind, rng):
    """nMSE and mean error of the linear code (basis Q, importances lam) at each rate on the samples (H, A)."""
    Z = (H - fr['m']) @ fr['Sm12']
    U = Z @ Q                       # components (P, n)
    out = []
    for r in rates:
        if kind == 'gauss':
            # water-filling of capacities: C_k = max(0, (1/2) log2(lam_k / theta)), sum C_k = r
            lo, hi = 1e-300, float(lam[0])
            for _ in range(200):
                mid = math.sqrt(lo * hi) if lo > 0 else hi / 2
                Ck = np.maximum(0.0, 0.5 * np.log2(np.maximum(lam, 1e-300) / mid))
                if Ck.sum() > r:
                    lo = mid
                else:
                    hi = mid
            Ck = np.maximum(0.0, 0.5 * np.log2(np.maximum(lam, 1e-300) / hi))
            snr = 2.0 ** (2 * Ck) - 1
            y = U + rng.standard_normal(U.shape) / np.sqrt(np.maximum(snr, 1e-300))
            Uh = np.where(snr > 0, y * (snr / (1 + snr)), 0.0)
            used = float(Ck.sum())
        else:
            bits = greedy_bits(lam, r)
            Uh = np.zeros_like(U)
            for k in np.nonzero(bits)[0]:
                Uh[:, k] = quantise(U[:, k], int(bits[k]))
            used = int(bits.sum())
        Hh = fr['m'] + (Uh @ Q.T) @ fr['S12']
        with torch.no_grad():
            Ah = net.run(torch.tensor(Hh, dtype=torch.float32), l).double().numpy()
        d = Ah - A
        e = (d * d).sum(1) / V
        md = d.mean(0)
        out.append(dict(rate=float(r), used=used, nmse=float(e.mean()), se=float(e.std() / math.sqrt(len(e))),
                        mean_err=float(md @ md) / V, mean_floor=float(d.var(0).sum()) / len(e) / V))
    return out
